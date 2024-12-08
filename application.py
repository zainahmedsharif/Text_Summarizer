#!/usr/bin/env python
# coding: utf-8


import os
from langchain.llms import OpenAI
from dotenv import load_dotenv
import docx
import fitz
from flask import Flask, request, render_template, redirect, url_for
from langchain.prompts import PromptTemplate


load_dotenv()



api_key = os.getenv("OPENAI_API_KEY")



llm = OpenAI(temperature=0.7, openai_api_key=api_key)


summary_template = """ 
Summarize the text below briefly:


{text}



"""

prompt = PromptTemplate(
    input_variables=["text"], 
    template=summary_template
)



def summarize_text(text):
    '''
    takes the input string and summarizes it using llm
    '''

    input_prompt = prompt.format(text=text)

    response = llm(input_prompt)

    return response


def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    return text


#
application = Flask(__name__)


@application.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if uploaded_file:
            file_type = uploaded_file.filename.split('.')[-1].lower()

            # Save the uploaded file to a temporary path
            file_path = os.path.join("temp", uploaded_file.filename)
            uploaded_file.save(file_path)

            # Extract text based on file type
            text = ""
            if file_type == "pdf":
                text = extract_text_from_pdf(file_path)
#            elif file_type == "docx":
#                text = extract_text_from_docx(file_path)
            elif file_type == "txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

            # Limit text size for API request
            if len(text) > 1000:
                text = text[:1000]

            # Get the summary
            summary = summarize_text(text)

            # Remove the temporary file after processing
            os.remove(file_path)

            # Render the summary result
            return render_template("index.html", summary=summary)

    return render_template("index.html", summary=None)

# Run the Flask server
if __name__ == "__main__":
    if not os.path.exists("temp"):
        os.makedirs("temp")
    application.run(host='0.0.0.0',port=5001)




