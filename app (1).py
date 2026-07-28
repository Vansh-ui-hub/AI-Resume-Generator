import streamlit as st 
# streamlit: Web Based app making
# lite python framework

st.title("AI Resume Maker")

st.markdown("""## User can create or download AI created Resume
based on high ATS Score""")

#====================== AGENT CODE============================
# STEP 2: Load Modules

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
from PIL import Image

#========================API KEY LOAD=========================

GOOGLE_API_KEY = st.sidebar.text_input("GOOGLE_API_KEY",type="password")
GROQ_API_KEY = st.sidebar.text_input("GROQ_API_KEY",type="password")
TAVILY_API_KEY = st.sidebar.text_input("TAVILY_API_KEY",type="password")

if not (GOOGLE_API_KEY) and not (GROQ_API_KEY) and not (TAVILY_API_KEY):
    st.sidebar.warning("PASS API KEYS")
    st.stop()
else:
    st.success("API KEYS LOADED")


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


prompt_generator(model)
# TOOL 2:
def resume_maker_prompt():
  """This function just gives updated prompt for model"""

  with open('prompt.py', 'r') as f:
    prompt = f.read()
  return prompt

resume_maker_prompt()


#=======================================UPLOAD IMAGE====================================================
uploaded_file = st.sidebar.file_uploader(
    "Choose an image file",
    type=["jpg","jpeg","png","webp"]
)
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)

        st.sidebar.image(image, caption="Uploaded image", use_container_width=True)

        if image.mode in ("RGBA", "P"):
           image= image.convert("RGB")
        base_name = os.path.splitext(uploaded_file.name)[0]
        save_path = f"{base_name}.jpg"

        #3. Save the image to the current working directory
        image.save(save_path, "JPEG")
        st.sidebar.success(f"🎉 image successfully saved as '{save_path}'!")

    except Exception as e:
        st.error(f"Error processing image: {e}")


#===============================GENERATE RESUME==============================

prompt="""You are a helpful AI assistant with job resume maker, your task
is to give HTML format resume, with proper designing using recent CSS and JS
code, with professional design format. User will upload data and return HTML
format resume, always use different styling use gradient theme pallete contrast in resume"""

IMPORTANT: wherever the profile photo goes in the resume, output exactly this tag and nothing else:

<img src="PROFILE_IMAGE_PLACEHOLDER" style="width:100px;height:100px;border-radius:50%;">
do not draw or generate any other image tag or placeholder circle yourself """
final_prompt=prompt+prompt_generator(model)
USER_INFO=st.text_input("ENTER YOUR INFORMATION")
user_details=f"""user details:given beow :resume info {USER_INFO} DEFAULT IF NOT GIVEN : PYTHON DEVELOPER RESUME """
query = final_prompt+user_details

import base64

if st.button('generate resume'):
  with st.spinner("runnign agent"):

    response = agent.invoke({'messages': [{'role':'user','content':query}]})
    print(response['messages'][-1].content)
    code=response['messages'][-1].content[-1]['text']

    # swap in the actual uploaded photo instead of the placeholder tag
    if uploaded_file is not None:
        with open(save_path, "rb") as img_file:
            b64_image = base64.b64encode(img_file.read()).decode()
        data_uri = f"data:image/jpeg;base64,{b64_image}"
        code = code.replace("PROFILE_IMAGE_PLACEHOLDER", data_uri)
    
   
    st.html(code, width="stretch", unsafe_allow_javascript=True)




