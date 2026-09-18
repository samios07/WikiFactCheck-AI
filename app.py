# 1. SETUP LIBRARIES (If running in Colab)
!pip install -q -U transformers accelerate gradio

# 2. IMPORTS & AUTHENTICATION
from transformers import pipeline
import gradio as gr
from google.colab import userdata
import os
import re

# Pull the token securely from Colab Secrets
os.environ["HF_TOKEN"] = userdata.get('HF_TOKEN')

# 3. BACKEND: LOAD GEMMA AI
pipe = pipeline("text-generation", model="google/gemma-2b-it", device_map="auto")

# 4. CORE LOGIC: THE FACT CHECKER (THE MATHEMATICAL ANCHOR)
def wiki_fact_check(infobox_fact, article_text):
    # 1. Parse the target safely
    if ":" in infobox_fact:
        topic = infobox_fact.split(":", 1)[0].strip()
        infobox_value = infobox_fact.split(":", 1)[1].strip()
    else:
        topic = "target information"
        infobox_value = infobox_fact.strip()

    # 2. AI Extraction
    prompt = f"""<start_of_turn>user
Based on the article text, what is the {topic}?
Keep it short.
Article: "{article_text}"<end_of_turn>
<start_of_turn>model
"""

    output = pipe(prompt, max_new_tokens=20, do_sample=False)
    ai_short_answer = output[0]['generated_text'].split("<start_of_turn>model")[-1].strip()
    ai_short_answer = ai_short_answer.split('\n')[0].replace('"', '').strip()

    # 3. PYTHON ANCHOR (The Word Intersection & HTML Fix)
    # Nuke all line breaks so HTML never breaks again
    clean_article = article_text.replace('\n', ' ')
    # Split purely by punctuation followed by spaces
    original_sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', clean_article) if s.strip()]

    anchored_sentence = ""

    # Mathematical Intersection: Check which original sentence shares the most words with the AI's answer.
    # This completely destroys the "AI paraphrasing" error.
    ai_words = set(re.findall(r'\b\w{4,}\b', ai_short_answer.lower())) # Grab words 4+ letters

    # Ensure it's not a generic AI refusal message
    if ai_words and "cannot" not in ai_short_answer.lower() and "context" not in ai_short_answer.lower():
        max_matches = 0
        for true_sentence in original_sentences:
            true_words = set(re.findall(r'\b\w{4,}\b', true_sentence.lower()))
            matches = len(ai_words.intersection(true_words))
            if matches > max_matches:
                max_matches = matches
                anchored_sentence = true_sentence

    # Failsafe: If the math fails, scan for the topic itself (e.g., "headquarters")
    if not anchored_sentence:
        for true_sentence in original_sentences:
            if topic.lower() in true_sentence.lower():
                anchored_sentence = true_sentence
                break

    if not anchored_sentence:
        anchored_sentence = "Could not definitively extract the context from the article."

    # 4. Logical Validation
    if infobox_value.lower() in anchored_sentence.lower() or infobox_value.lower() in article_text.lower():
        return "✅ **Facts align. No mismatch detected.**"

    # Clean UI generation
    return f"""⚠️ **Possible mismatch detected.**

* **Infobox Value:** {infobox_fact}
* **Article Value:** <span style="color: #22c55e; font-weight: bold; text-transform: uppercase;">{anchored_sentence}</span>

* **💡 AI Suggestion:** Please cross-reference this discrepancy with primary Wikipedia citations to verify the correct information."""

# 5. FRONTEND: GRADIO UI
app = gr.Interface(
    fn=wiki_fact_check,
    inputs=[
        gr.Textbox(lines=2, label="1. Structured Fact (Infobox)", placeholder="e.g., Release Date: 15 July 2020"),
        gr.Textbox(lines=7, label="2. Main Article Text", placeholder="Paste the Wikipedia article paragraph here...")
    ],
    # Fixed the invisible box bug by adding a default placeholder
    outputs=gr.Markdown(
        value="*Waiting for submission. The report will appear here...*",
        label="Fact-Check Report & AI Suggestion"
    ),
    title="WikiFact Check AI",
    description="Detects mismatches between structured data and article text for human verification."
)

# 6. LAUNCH APP
app.launch(share=True)
