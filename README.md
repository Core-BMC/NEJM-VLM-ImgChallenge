# NEJM VLM Image Challenge

---

## Overview

This project utilizes vision models and vision large language models (VLMs) to analyze and solve medical image challenges from [the **New England Journal of Medicine** (NEJM) **Image Challenge**](https://www.nejm.org/image-challenge). The goal is to leverage advanced vision models to interpret medical images and provide educational insights.

## Table of Contents

- [NEJM VLM Image Challenge](#nejm-vlm-image-challenge)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [License](#license)
  - [Contact](#contact)
  - [Acknowledgements](#acknowledgements)

## Installation

Follow these steps to install the project:

1. Clone the repository:

   ```bash
   git clone https://github.com/Core-BMC/NEJM-VLM-ImgChallenge.git
   ```

2. Navigate into the project directory:

   ```bash
   cd NEJM-VLM-ImgChallenge
   ```

3. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
    - On Windows:
      ```bash
      .\venv\Scripts\activate
      ```

    - On macOS and Linux:
      ```bash
      source venv/bin/activate
      ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```


## Usage

Follow these steps to run the project:

1. **Data Preparation**: (0.x Data Preparation Files)

   - Input: `NEJM_Question.pptx`
   - Output: `NEJM_list.xlsx`, `pptimages` (folder)
   - The `NEJM_Question.pptx` file was prepared by downloading PowerPoint slides from the [NEJM Image Challenge website](https://www.nejm.org/image-challenge). This file binds together the question slides (first page) from each downloaded PowerPoint slide set.
   - Extract text and images from `NEJM_Question.pptx` and save text to `NEJM_list.xlsx` and images to `pptimages` folder.

      **Note:** We provide a code that processes the `NEJM_Question.pptx` file to extract images and text into the pptimages folder and `NEJM_list.xlsx` file. Subsequently, `NEJM_list.xlsx` includes radiologists' labels and section information regarding the modality and body part of the image challenge (paper in process).
  
    Place your PPTX file in the same directory as the script. Ensure the file name is `NEJM_Question.pptx`.

    ```bash
      python 0.NEJM_pptx_preproc.py
    ```


1s. **Local Environment Setup**

  - If API keys are already configured in the environment
      Nothing to do.

  - Environment-specific configuration using python-dotenv
      
    1. Install the python-dotenv library:
      
        ```bash
        pip install python-dotenv
        ```
    2. Set up a `.env` file in the root directory of your project.
    3. Open the .env file and paste in your secret API keys as follows:
       ```.env
       OPENAI_API_KEY=sk-12345678901234567890
       GOOGLE_API_KEY=AI12345678901234567890
       ANTHROPIC_API_KEY=sk-ant-api12-34567890
       ```
    4. Open your Python file and add the following code to load the environment variables:
       ```python
       import os
       from dotenv import load_dotenv

       load_dotenv()

       OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
       GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
       ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
       ```


2. **OPENAI GPT**: (1.1.x request to OpenAI GPT vision model)

   - Input: `NEJM_list.xlsx`, `pptimages` (folder)
   - Run `1.1.1.gpt4v-NEJM-ImgChallenge.py`
     - Output: `gpt4v_result` (folder)
   - Run `1.1.2.gpt4o-NEJM-ImgChallenge.py`
     - Output: `gpt4o_result` (folder)

3. **Gemini**: (1.2.x request to Google Gemini vision model)

   - Input: `NEJM_list.xlsx`, `pptimages` (folder)
   - Run `1.2.1.gemini1.5-pro-NEJM-ImgChallenge.py`
     - Output: `gemini_result` (folder)
   - (Not used in the paper) Run `1.2.2.gemini1.5-flash-NEJM-ImgChallenge.py`
     - Output: `gemini_flash_result` (folder)

4. **Claude**: (1.3 request to Anthropic Claude 3 Opus vision model)

   - Input: `NEJM_list.xlsx`, `pptimages` (folder)
   - Run `1.3.claude3v-opus-NEJM-ImgChallenge.py`
     - Output: `Claude_result` (folder)

5. **Data Integration**:
   - Input: `*_result` (folders)
   - Run `2.VLM-results-integration.py`
     - Output: `combined_sum.xlsx`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

Woo Hyun Shim - [swh@amc.seoul.kr](mailto:swh@amc.seoul.kr)

[Hwon Heo](https://github.com/hwonheo) - [heohwon@gmail.com](mailto:heohwon@gmail.com)


Project Link: [https://github.com/Core-BMC/NEJM-VLM-ImgChallenge](https://github.com/Core-BMC/NEJM-VLM-ImgChallenge)


---

## Acknowledgements

This project was inspired by the [NEJM Image Challenge](https://www.nejm.org/image-challenge). Special thanks to the NEJM team for providing the challenging and educational content.
