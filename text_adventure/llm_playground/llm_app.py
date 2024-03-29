import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import OpenAI

load_dotenv()

st.title(':rainbow[_Basic LLM_]')

with st.sidebar:
    openai_api_key = st.text_input('OpenAI API Key', type='password', value=os.getenv("OPENAI_API_KEY"))


def generate_response(input):
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    st.info(llm(input))


with st.form('input_form', border=True):
    input = st.text_area('Your input:', 'Think of something to ask the LLM.')
    submitted = st.form_submit_button()
    if not openai_api_key.startswith('sk-'):
        st.warning('Enter an API key.', icon='🔑')
    if submitted and openai_api_key.startswith('sk-'):
        generate_response(input)