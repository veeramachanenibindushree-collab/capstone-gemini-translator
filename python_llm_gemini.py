import streamlit as st
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv
from gtts import gTTS
import os
import pandas as pd
import PyPDF2
import tempfile



# Set up the Google Generative AI API key
#genai.configure(api_key="AIzaSyDFN9zCMHobDIl0Z0_in4DjcOuUkVdH9YY")
#model = genai.GenerativeModel("gemini-1.5-flash")
#model

# Load API key from environment variable

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
model

#Function : Translate text using Google Generative AI
def translate_text(text, target_language):
    try:
        prompt = f"Translate the following text into {target_language}. Provide only the translated text:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error during translation: {e}"
    

# Function : Extract text from uploaded files
def extract_text_from_file(uploaded_file):
    if uploaded_file.name.endswith('.pdf'):
        with tempfile.NamedTemporaryFile(delete=False, suffix='/pdf') as temp_file:
            temp_file.wrire(uploaded_file.getbuffer())
            with open(temp_file.name, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + '\n'
        os.remove(temp_file.name)
        return text
    elif uploaded_file.name.endswith('.txt'):
        return uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        return " ".join(df.astype(str).value.flatten())
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
        return " ".join(df.astype(str).value.flatten()) 
    else:
        return "Unsupported file format. Please upload a PDF or TXT,CSV or XLSX file format alone."
    

# Function : Convert text to speech
def text_to_speech(text, language='en'):
    try:
        tts = gTTS(text=text, lang=language)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            return temp_file.name
    except Exception as e:
        return f"Error during text-to-speech conversion: {e}"
    


# Streamlit app UI
st.set_page_config(page_title="Google Gemini Translation and Text-to-Speech App", page_icon=":globe_with_meridians:",layout="wide")
st.title("Google Gemini translation and Text-to-Speech App")  
st.write("This app allows you to translate text using Google Gemini and convert it to speech. You can upload a file or enter text directly.")

#Text input or file upload
text_input = st.text_area("Enter text to translate:" , )
uploaded_file = st.file_uploader("Or upload a file (PDF, TXT, CSV, XLSX):", type=["pdf", "txt","csv","xlsx"])
language = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Chinese (Simplified)': 'zh-CN',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Hindi': 'hi',
    'Arabic': 'ar'
}

selected_language = st.selectbox("Select target language for translation:", list(language.keys()))

if st.button("Translate"):
    #Get text from input or uploaded file
    if uploaded_file is not None:
        text = extract_text_from_file(uploaded_file)
    elif text_input:
        text = text_input

    #Validate text input
    if text.strip() == "":
        st.error("Please provide text to translate.")
    else:
        #Translate using Gemini
        translated_text = translate_text(text, selected_language)
        st.subheader("Translated Text:")
        st.write(translated_text)

        # Convert translated text to speech
        audio_file = text_to_speech(translated_text, language=language[selected_language]) 
        if audio_file:
            st.audio(audio_file, format='audio/mp3')
            with open(audio_file, 'rb') as f:
                st.download_button('Download Audio', f, file_name='translated_audio.mp3', mime='audio/mp3')
        else:
            st.error("Error generating audio file.")