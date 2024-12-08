#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from langchain.llms import OpenAI
from dotenv import load_dotenv
import docx
import fitz
from flask import Flask, request, render_template, redirect, url_for


# In[2]:


load_dotenv()


# In[3]:


api_key = os.getenv("OPENAI_API_KEY")


# In[ ]:





# In[4]:


llm = OpenAI(temperature=0.7, openai_api_key=api_key)


# In[5]:


from langchain.prompts import PromptTemplate


# In[6]:


summary_template = """ 
Summarize the text below briefly:


{text}



"""


# In[7]:


prompt = PromptTemplate(
    input_variables=["text"], 
    template=summary_template
)


# In[8]:


def summarize_text(text):
    '''
    takes the input string and summarizes it using llm
    '''

    input_prompt = prompt.format(text=text)

    response = llm(input_prompt)

    return response


# In[9]:


summarize_text("When interacting with the API some actions such as starting a Run and adding files to vector stores are asynchronous and take time to complete. The SDK includes helper functions which will poll the status until it reaches a terminal state and then return the resulting object. If an API method results in an action that could benefit from polling there will be a corresponding version of the method ending in '_and_poll'.")


# In[ ]:





# In[ ]:





# In[10]:


def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    return text


# In[11]:


application = Flask(__name__)


# In[12]:


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
            elif file_type == "docx":
                text = extract_text_from_docx(file_path)
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


# In[ ]:




