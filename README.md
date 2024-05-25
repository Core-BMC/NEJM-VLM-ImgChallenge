# NEJM VLM Image Challenge #1

Text and Image

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

1. **Data Preparation**: (0.x 데이터 준비 파일들)

   - Input: `NEJM_Question.pptx`
   - Output: `NEJM_list.xlsx`, `pptimages` (folder)
   - Extract text and images from `NEJM_Question.pptx` and save text to `NEJM_list.xlsx` and images to `pptimages` folder.
   - NEJM_Question.pptx에서 text와 image를 추출해서 text는 NEJM_list.xlsx로 저장하고, image는 pptimages에 저장한다. 이 작업 내용은 데이터 전처리 파트라 github에 안올려도 될 듯.

2. **OPENAI GPT**:

   - Input: `NEJM_list.xlsx`, `pptimages` (folder)
   - Run `1.1.1.GPT4v에전송.py`
     - Output: `gpt4v_result` (folder)
   - Run `1.1.2.GPT4v에전송gpt4o.py`
     - Output: `gpt4o_result` (folder)

3. **Gemini (GOOGLE API key needs to be removed before upload)**:

   - Input: `NEJM_list.xlsx`, `pptimages` (folder)
   - Run `1.2.1.Gemini에_history_영상_전송개발완료.py`
     - Output: `gemini_result` (folder)
   - (Not used in the paper) Run `1.2.2.Gemini에_history_영상_전송개발완료_flash.py`
     - Output: `gemini_flash_result` (folder)

4. **Claude**:

   - Input: `NEJM_list.xlsx`, `pptimages` (folder)
   - Run `1.3.ClaudeV에전송.py`
     - Output: `Claude_result` (folder)

5. **Data Integration**:
   - Input: `XXX_result` (folders)
   - Run `2.GPT.Gemini.txt결과를엑셀로정리.py`
     - Output: `combined_sum.xlsx`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

Woo Hyun Shim - [swh@amc.seoul.kr](mailto:swh@amc.seoul.kr)

Project Link: [https://github.com/yourusername/yourproject](https://github.com/yourusername/yourproject)
