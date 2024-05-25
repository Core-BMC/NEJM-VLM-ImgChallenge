# NEJM VLM Image Challenge

---

### Project Overview

This project utilizes vision models and vision large language models (VLMs) to analyze and solve medical image challenges from the New England Journal of Medicine (NEJM) Image Challenge. The goal is to leverage advanced AI models to interpret medical images and provide educational insights.

## Table of Contents

- [NEJM VLM Image Challenge #1](#nejm-vlm-image-challenge-1)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [License](#license)
  - [Contact](#contact)

## Installation

Follow these steps to install the project:

1. Clone the repository:

   ```bash
   git clone https://github.com/Core-BMC/NEJM-VLM-ImgChallenge.git
   ```

2. Navigate into the project directory and install the required packages:

   ```bash
   cd NEJM-VLM-ImgChallenge
   pip install -r requirements.txt
   ```

## Usage

Follow these steps to run the project:

1. **Data Preparation**: (0.x Data Preparation Files)

   - Input: `NEJM_Question.pptx`
   - Output: `NEJM_list.xlsx`, `pptimages` (folder)
   - The `NEJM_Question.pptx` file was prepared by downloading PowerPoint slides from the [NEJM Image Challenge website](https://www.nejm.org/image-challenge). This file binds together the question slides (first page) from each downloaded PowerPoint slide set.
   - Extract text and images from `NEJM_Question.pptx` and save text to `NEJM_list.xlsx` and images to `pptimages` folder.

2. **OPENAI GPT**: (1.1.x request to OpenAI GPT vision model)

   - Input: `NEJM_list.xlsx`, `pptimages` (folder)
   - Run `1.1.1.gpt4v-NEJM-ImgChallenge.py`
     - Output: `gpt4v_result` (folder)
   - Run `1.1.2.gpt4o-NEJM-ImgChallenge.py`
     - Output: `gpt4o_result` (folder)

3. **Gemini**: (1.2.x request to Google Gemini vision model)

   - Input: `NEJM_list.xlsx`, `pptimages` (folder)
   - Run `1.2.1.gemini-NEJM-ImgChallenge.py`
     - Output: `gemini_result` (folder)
   - (Not used in the paper) Run `1.2.2.gemini_flash-NEJM-ImgChallenge.py`
     - Output: `gemini_flash_result` (folder)

4. **Claude**: (1.3 request to Anthropic Claude 3 Opus vision model)

   - Input: `NEJM_list.xlsx`, `pptimages` (folder)
   - Run `1.3.ClaudeV-NEJM-ImgChallenge.py`
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
