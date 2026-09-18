# WikiFact Check AI 🕵️‍♂️
An automated, anti-hallucination fact-checking tool using Gemma-2B and deterministic mathematical text anchoring.

### ⚠️ Live Demo & Hosting Notice
**Note:** Due to Hugging Face recently paywalling Gradio compute spaces, the live web app is hosted via Google Colab. The standard `gradio.live` link is only active while the local Colab session is running. 

**Please view the full functional video demonstration below:**


https://github.com/user-attachments/assets/5052001a-a2e6-49dc-a42e-a494e7d122e9





---

### 🧠 The Technical Architecture
Standard AI fact-checking pipelines suffer from hallucination—LLMs often rewrite source material or paraphrase details, making it impossible to verify exact quotes. This project solves that vulnerability using a hybrid AI/Python architecture:

* **Blind Semantic Extraction:** Google's `gemma-2b-it` is deployed via Hugging Face Transformers. The AI is denied access to the structured infobox data to prevent confirmation bias; its only job is to generate a low-token semantic guess of where the answer lives in the main text.
* **Text Sanitization:** A Python regex pipeline physically strips hidden paragraph breaks (`\n`) from the messy Wikipedia data to prevent HTML DOM rendering failures in the frontend.
* **Deterministic Mathematical Anchoring:** To prevent the 2B model from successfully paraphrasing the answer, a custom Python `set().intersection()` algorithm mathematically compares the AI's output tokens against the original text. The original sentence with the highest word intersection is anchored. 
* **Boolean Validation:** Once isolated, Python executes a strict Boolean substring check against the Infobox data, completely bypassing the language model for the final verification step.

### ⚙️ Built With
* Python
* Google `gemma-2b-it`
* Hugging Face Transformers
* Gradio (UI Framework)
* Custom CSS String Injection


Developed By: SAMANYU P & JEEVAN N G
University: SAPTHAGIRI NPS UNIVERSITY
