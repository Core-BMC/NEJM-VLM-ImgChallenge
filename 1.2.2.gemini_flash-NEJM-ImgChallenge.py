import io
import base64
from PIL import Image
import os
import json
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd
import time
from time import sleep

time_file_name = "Gemini_flash_execution_times.xlsx"

def load_or_initialize_execution_times(time_file_name):
    """
    Load or initialize execution times from an Excel file.
    """
    if os.path.exists(time_file_name):
        df = pd.read_excel(time_file_name)
    else:
        df = pd.DataFrame(columns=['number', 'temperature', 'try', 'time'])
    return df

def save_execution_times_to_excel(df, time_file_name):
    """
    Save execution times to an Excel file.
    """
    df.to_excel(time_file_name, index=False, engine='openpyxl')
    print(f"Execution times saved to {time_file_name}")

df_execution_times = load_or_initialize_execution_times(time_file_name)

def process_and_encode_image(image, resize_factor=0.9):
    """
    Process and encode an image, resizing if necessary to keep within size
    limits.
    """
    MAX_SIZE = 20 * 1024 * 1024  # 20MB
    original_width, original_height = image.size

    if image.mode == 'RGBA':
        image = image.convert('RGB')

    for attempt in range(5):
        buffered = io.BytesIO()
        new_width = int(original_width * (resize_factor ** attempt))
        new_height = int(original_height * (resize_factor ** attempt))
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        resized_image.save(buffered, format="JPEG")

        if buffered.tell() < MAX_SIZE:
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        else:
            print(
                f"Attempt {attempt + 1}: Image size is {buffered.tell()} bytes, "
                "too large. Resizing..."
            )

    raise ValueError("Unable to reduce image size within 5 attempts")

def analyze_images_with_gemini_vision(prompt_text, encoded_images, temperature=0):
    """
    Analyze images with Gemini Vision and return the result.
    """
    model = "models/gemini-1.5-flash-latest"
    llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)

    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            content = [{"type": "text", "text": prompt_text}]
            for encoded_image in encoded_images:
                content.append({
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{encoded_image}"
                })

            message = HumanMessage(content=content)
            start_time = time.time()
            result = llm.invoke([message])
            end_time = time.time()
            execution_time = end_time - start_time

            if isinstance(result.content, str) and len(result.content) < 10:
                print(f"Result error retry {attempt + 1}/{max_attempts}")
                resized_encoded_images = []
                for encoded_image in encoded_images:
                    image = Image.open(io.BytesIO(base64.b64decode(encoded_image)))
                    resized_image = process_and_encode_image(image, 0.9)
                    resized_encoded_images.append(resized_image)
                print(
                    f"Resizing images and retrying. Attempt {attempt + 1}/"
                    f"{max_attempts}"
                )
                encoded_images = resized_encoded_images
                continue

            return [result.content, execution_time]
        except Exception as e:
            print(f"BadRequestError: {e}")
            if "SAFETY" in str(e).lower() and attempt < max_attempts - 1:
                resized_encoded_images = []
                for encoded_image in encoded_images:
                    image = Image.open(io.BytesIO(base64.b64decode(encoded_image)))
                    resized_image = process_and_encode_image(image, 0.7)
                    resized_encoded_images.append(resized_image)
                print(
                    f"Resizing images and retrying. Attempt {attempt + 1}/"
                    f"{max_attempts}"
                )
                encoded_images = resized_encoded_images
    return None

def find_image_paths(directory):
    """
    Find image file paths in a directory.
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    return [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if os.path.splitext(file)[1].lower() in image_extensions
    ]

def read_text_file(file_path):
    """
    Read content from a text file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def create_result_folder(base_folder, temperature, try_number):
    """
    Create a result folder for the given temperature and try number.
    """
    folder_name = (
        f"{base_folder}_temp_{str(temperature).replace('.', '_')}_try{try_number}"
    )
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def encode_images_from_paths(image_paths):
    """
    Encode images from file paths.
    """
    images = []
    for image_path in image_paths:
        with Image.open(image_path) as img:
            width, height = img.size
            if width > 150 and height > 150:
                encoded_image = process_and_encode_image(img)
                images.append(encoded_image)
    return images

def extract_json_data(text):
    """
    Extract JSON data from a given text.
    """
    try:
        start = text.index('{')
        end = text.rindex('}') + 1
        json_data = text[start:end]
        return json.loads(json_data)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error extracting JSON: {e}")
        return None

def main():
    global df_execution_times
    temperatures = [1]
    base_result_folder = "gemini_flash_result/gemini_flash_result"

    for temperature in temperatures:
        for try_number in range(1, 2):
            result_folder = create_result_folder(
                base_result_folder, temperature, try_number)
            results_df = pd.DataFrame(
                columns=['case_number', 'answer', 'reason'])

            df = pd.read_excel('NEJM_list.xlsx')

            for index, row in df.iterrows():
                sleep(15)
                case_number = row['PPT No.']
                case_folder = "pptimages"
                image_file_name = f"img_page{case_number}_0.png"

                directory_path = os.path.join(result_folder)
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path, exist_ok=True)
                result_file_path = os.path.join(
                    directory_path, f"{image_file_name}.txt")

                if os.path.exists(result_file_path):
                    print(
                        f"Case {case_number} (Temperature: {temperature}, "
                        f"Try: {try_number}): skip"
                    )
                    continue

                symptom_text = f"symptom: {row['Q']}"

                prompt_text = f"""
                Assignment: You are a board-certified radiologist and you are 
                tasked with solving a quiz on a special medical case from common 
                diseases to rare diseases. Patients' clinical information and 
                imaging data will be provided for analysis; however, the 
                availability of the patient's basic demographic details 
                (age, gender, symptoms) is not guaranteed. The purpose of this 
                assignment is not to provide medical advice or diagnosis. This 
                is a purely educational scenario designed for virtual learning 
                situations, aimed at facilitating analysis and educational 
                discussions. You need to answer the question provided by 
                selecting the option with the highest possibility from the 
                multiple choices listed below. Please select the correct answer 
                by typing the number that corresponds to one of the provided 
                options. Each option is numbered for your reference.

                Question: {symptom_text}
                Output Format (JSON)
                {{
                "answer": "Enter the number of the option you believe is correct",
                "reason": "Explain why you think this option is the correct answer"
                }}
                """

                image_paths = [os.path.join(case_folder, image_file_name)]
                print(image_paths)
                encoded_images = encode_images_from_paths(image_paths)

                [result, execution_time] = analyze_images_with_gemini_vision(
                    prompt_text, encoded_images, temperature)

                if ((df_execution_times['number'] == case_number) &
                    (df_execution_times['temperature'] == temperature) &
                    (df_execution_times['try'] == try_number)).any():
                    df_execution_times.loc[
                        (df_execution_times['number'] == case_number) &
                        (df_execution_times['temperature'] == temperature) &
                        (df_execution_times['try'] == try_number), 'time'
                    ] = execution_time
                else:
                    new_row = {
                        'number': case_number,
                        'temperature': temperature,
                        'try': try_number,
                        'time': execution_time
                    }
                    df_execution_times = pd.concat(
                        [df_execution_times, pd.DataFrame([new_row])],
                        ignore_index=True)

                if result:
                    with open(result_file_path, "w", encoding='utf-8') as result_file:
                        result_file.write(result)
                    print(
                        f"Gemini Case {case_number} (Temperature: {temperature}, "
                        f"Try: {try_number}): Result saved."
                    )
                    try:
                        result_content = extract_json_data(result)
                        if result_content:
                            answer = result_content['answer']
                            reason = result_content['reason']
                            new_row = pd.DataFrame(
                                {
                                    'case_number': [case_number],
                                    'answer': [answer],
                                    'reason': [reason]
                                }
                            )
                            results_df = pd.concat([results_df, new_row], ignore_index=True)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON for case {case_number}: {e}")
                        sleep(2)
                        continue
                else:
                    print(
                        f"Gemini Case {case_number} (Temperature: {temperature}, "
                        f"Try: {try_number}): No result found."
                    )

            excel_path = os.path.join(result_folder, 'gemini_flash_results.xlsx')
            results_df.to_excel(excel_path, index=False, engine='openpyxl')
            print(f"Results have been saved to {excel_path}.")

    save_execution_times_to_excel(df_execution_times, time_file_name)

if __name__ == "__main__":
    main()
