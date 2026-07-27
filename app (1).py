import streamlit as st 
# streamlit: Web Based app making
# lite python framework

st.title("AI Resume Maker")

st.markdown("""## User can create or download AI created Resume
based on high ATS Score""")

#====================== AGENT CODE============================
# STEP 2: Load Modules
import IPython as ip
import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
from langchain.messages import SystemMessage, HumanMessage
import numpy as np
import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader


#========================API KEY LOAD=========================

GOOGLE_API_KEY = st.sidebar.text_input("GOOGLE_API_KEY",type="password")
GROQ_API_KEY = st.sidebar.text_input("GROQ_API_KEY",type="password")
TAVILY_API_KEY = st.sidebar.text_input("TAVILY_API_KEY",type="password")


#========================MODEL BUILDING=========================


model = ChatGoogleGenerativeAI(
    model='gemini-3.5-flash-lite',
    google_api_key = GOOGLE_API_KEY
)

# TOOL
def search_recent_news_jobs(query):
  """This function is helps to search recent news or recent jobs
  related to given search query suppose user write python developer jobs
  It should return trending news and jobs link"""
  client = TavilyClient(api_key= TAVILY_API_KEY)
  return client.search(query)


# Agent Creation
from langchain.agents import create_agent
agent = create_agent(
  model=model,
    tools= [search_recent_news_jobs] # user can give multiple tools
)



#========================PROMPT GENERATOR=========================

def prompt_generator(agent):
  """ This function helps to give detailed prompt followed by chain of thoughts
   and persona based prompting, main task is to give detailed prompt to build resume for students or Experienced
   person Based on their given personal information"""

  prompt = """You are a senior HR resume analyzer,
  main task is to give detailed prompt to build resume for
  students or Experienced
  person Based on their given personal information.
  System Instruction I want to
  generate resume in HTML format include that in prompt"""

  response = agent.invoke(prompt)
  file_name = 'prompt.py'
  with open(file_name, 'w') as f:
    f.write(response.content [-1] ['text'])
  return "Prompt file generated Successfully, agent can read it"



# TOOL 2:
def resume_maker_prompt():
  """This function just gives updated prompt for model"""

  with open('prompt.py', 'r') as f:
    prompt = f.read()
  return prompt


#===============================GENERATE RESUME==============================

prompt = """You are a helpful AI assistant with job resume maker, your task
is to give HTML format resume, with proper designing using recent CSS and JS
code, with professional design format. user will upload data and return HTML
format resume"""

final_prompt = prompt + resume_maker_prompt()
user_details = """User details: given below:
TANVI JAIN, +91 7048931461, jaintanvi770@gmail.com
Naveen Shahdara, Delhi DOB 17-01-2008
Skills: Python,Web developing, canva Expert, Sql
Languages: Hindi, english
Education: IITM university
Bachelor of Computer Application
Give Python Developer Resume, always use different styling use gradient theme pallete contrast in resume"""

query = final_prompt + user_details

if st.button("Generate Resume"):
  with st.spinner("Running Agent...."):
    
    response = agent.invoke({'messages': [{'role': 'user',"content": query}]})
    code = response['messages'] [-1].content [-1] ['text']
    
    st.markdown(code)




def resu