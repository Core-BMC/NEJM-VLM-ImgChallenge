import io
import base64
import json
from PIL import Image
import os
import sys
import time
import statistics
import pandas as pd
import anthropic
from time import sleep

client = anthropic.Anthropic()

# List to record execution times
execution_times = []
time_file_name = "Claude_execution_times.xlsx"

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

# Load or initialize the execution times DataFrame
df_execution_times = load_or_initialize_execution_times(time_file_name)

# Initialize log file path
log_file_path = os.path.join("./", "process_log.txt")

def log_message(message):
    """
    Log a message to the console and a log file.
    """
    print(message)
    with open(log_file_path, "a") as log_file:
        log_file.write(message + "\n")

def process_and_encode_image(image, resize_factor=0.9):
    """
    Process and encode an image, resizing if necessary to keep within size limits.
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
            print(f"Attempt {attempt + 1}: Image size is {buffered.tell()} bytes, too large. Resizing...")

    raise ValueError("Unable to reduce image size within 5 attempts")

def analyze_images_with_claude_vision(prompt_text, encoded_images, temperature=0):
    """
    Analyze images with Claude Vision and return the result.
    """
    client = anthropic.Client(
        api_key=os.getenv("ANTHROPIC_API_KEY"))
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            image_contents = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": encoded_image
                    }
                } for encoded_image in encoded_images
            ]
            start_time = time.time()
            response = client.messages.create(
                model="claude-3-opus-20240229",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            #*image_contents
                        ],
                    }
                ],
                max_tokens=1024,
                temperature=temperature,
            )
            response_result = response

            if response_result.content[0].text.startswith("I'm sorry, but"):
                print(f"I'm sorry retry {attempt + 1}/{max_attempts}")
                continue

            end_time = time.time()
            execution_time = end_time - start_time
            execution_times.append(execution_time)

            average_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)
            std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0

            total_data_points = len(execution_times)

            print(f"Total data points: {total_data_points}")
            print(f"Average execution time: {average_time:.2f} seconds")
            print(f"Max execution time: {max_time:.2f} seconds")
            print(f"Min execution time: {min_time:.2f} seconds")
            print(f"Standard deviation: {std_dev:.2f} seconds")

            return response_result.content[0].text
        except Exception as e:
            print(f"BadRequestError: {e}")
            if "exceeded" in str(e).lower():
                save_execution_times_to_excel(df_execution_times, time_file_name)
                sys.exit()
            if "image_parse_error" in str(e).lower() and attempt < max_attempts - 1:
                resized_encoded_images = []
                for encoded_image in encoded_images:
                    image = Image.open(io.BytesIO(base64.b64decode(encoded_image)))
                    resized_image = process_and_encode_image(image, 0.9)
                    resized_encoded_images.append(resized_image)
                print(f"Resizing images and retrying. Attempt {attempt + 1}/{max_attempts}")
                encoded_images = resized_encoded_images
            
    return None

def find_image_paths(directory):
    """
    Find image file paths in a directory.
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    return [os.path.join(directory, file) for file in os.listdir(directory) if os.path.splitext(file)[1].lower() in image_extensions]

def read_text_file(file_path):
    """
    Read content from a text file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

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

def create_result_folder(base_folder, temperature, try_number):
    """
    Create a result folder for the given temperature and try number.
    """
    folder_name = f"{base_folder}_temp_{str(temperature).replace('.', '_')}_try{try_number}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def main():
    global df_execution_times
    temperatures = [1]
    base_result_folder = "Claude_result/Claude_result"

    for temperature in temperatures:
        for try_number in range(1, 2):
            result_folder = create_result_folder(base_result_folder, temperature, try_number)
            results_df = pd.DataFrame(columns=['case_number', 'answer', 'reason'])

            df = pd.read_excel('NEJM_list.xlsx')

            for index, row in df.iterrows():
                case_number = row['PPT No.']
                case_folder = "pptimages"
                image_file_name = f"img_page{case_number}_0.png"

                directory_path = os.path.join(result_folder)
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path, exist_ok=True)
                result_file_path = os.path.join(directory_path, f"{image_file_name}.txt")

                if os.path.exists(result_file_path):
                    print(f"Case {case_number} (Temperature: {temperature}, Try: {try_number}): skip")
                    continue

                symptom_text = f"symptom: {row['Q']}"

                prompt_text = f"""
                Assignment: You are a board-certified radiologist and you are tasked with solving a quiz on a special medical case from common diseases to rare diseases.
                Patients' clinical information and imaging data will be provided for analysis; however, the availability of the patient's basic demographic details (age, gender, symptoms) is not guaranteed.
                The purpose of this assignment is not to provide medical advice or diagnosis.
                This is a purely educational scenario designed for virtual learning situations, aimed at facilitating analysis and educational discussions.
                You need to answer the question provided by selecting the option with the highest possibility from the multiple choices listed below.
                Please select the correct answer by typing the number that corresponds to one of the provided options. Each option is numbered for your reference.

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
                
                start_time = time.time()
                result = analyze_images_with_claude_vision(prompt_text, encoded_images, temperature)
                end_time = time.time()
                execution_time = end_time - start_time

                if ((df_execution_times['number'] == case_number) &
                    (df_execution_times['temperature'] == temperature) &
                    (df_execution_times['try'] == try_number)).any():
                    df_execution_times.loc[(df_execution_times['number'] == case_number) &
                                           (df_execution_times['temperature'] == temperature) &
                                           (df_execution_times['try'] == try_number), 'time'] = execution_time
                else:
                    new_row = {'number': case_number, 'temperature': temperature, 'try': try_number, 'time': execution_time}
                    df_execution_times = pd.concat([df_execution_times, pd.DataFrame([new_row])], ignore_index=True)

                print(result)
                if result:
                    with open(result_file_path, "w", encoding='utf-8') as result_file:
                        result_file.write(result)
                    print(f"Case {case_number} (Temperature: {temperature}, Try: {try_number}): Result saved.")
                    try:
                        result_content = json.loads(result)
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
                    print(f"Case {case_number} (Temperature: {temperature}, Try: {try_number}): No result found.")
                    log_message(f"Case {case_number} (Temperature: {temperature}, Try: {try_number}): No result found.")

            excel_path = os.path.join(result_folder, 'claude_results.xlsx')
            results_df.to_excel(excel_path, index=False, engine='openpyxl')
            print(f"Results have been saved to {excel_path}.")

    save_execution_times_to_excel(df_execution_times, time_file_name)

if __name__ == "__main__":
    main()
