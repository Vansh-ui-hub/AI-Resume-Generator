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

prompt="""You are an expert ATS Resume Writer and Professional Resume Designer.

Generate a modern, premium, ATS-friendly resume using only HTML and CSS.

Requirements:
- Clean, elegant, recruiter-friendly design.
- Fully responsive, single-page layout.
- Excellent typography, spacing, alignment, and white space.
- Professional color palette (White, Navy, Gray) with subtle accents.
- Modern cards, icons (Font Awesome CDN), and section dividers.
- Include: Profile, Contact, Summary, Education, Experience, Projects, Skills, Certifications, Achievements, Languages, Interests, References (if provided).
- Display skills as tags or progress bars.
- Highlight achievements with bullet points.
- Keep ATS compatibility (semantic HTML, readable text, no tables for layout).
- Handle missing fields gracefully by hiding empty sections.
- Use this image tag only where profile photo is required:

<img src="PROFILE_IMAGE_PLACEHOLDER" style="width:120px;height:120px;border-radius:50%;object-fit:cover;">

- Never generate any other image tag.
- Return only a complete HTML document with embedded CSS.
- Do not include explanations, markdown, or code fences.
- Make every resume unique, visually impressive, and suitable for internships, freshers, and experienced professionals. """

final_prompt=prompt+prompt_generator(model)
USER_INFO=st.text_area("ENTER YOUR INFORMATION")
user_details= f"""user details:given beow :
Resume info {USER_INFO}
Photo: {uploaded_file }
Photo present in current directory with name as 
uploaded_file, and once resume generated give
download button in same html code.
DEFAULT IF NOT GIVEN : PYTHON DEVELOPER RESUME """
query = final_prompt+user_details

import base64


OPTIONS = ["DELHI","NOIDA","GURGAON/GURUGRAM",
           "KANPUR","LUCKNOW","BANGLORE","PUNE"]
LOCATION = st.sidebar.multiselect('SELECT LOCATION: ',
                                  options=OPTIONS)
JOB_PROFILE=["PYTHON DEVELOPER","GEN AI","FULL-STACK DEVELOPER","DATA ANALYST"]

PROFILE= st.sidebar.multiselect('SELECT JOB ROLE: ',
                                  options=JOB_PROFILE)


job_prompt= f"""Based on (PROFILE) jobs in {LOCATION}, I
want latest job news in using tavily,
try top 10 search or whatever available
and give result like naukri theme design with
job name, job desc, salary,
apply link and OUTPUT must be in HTML no markdown"""


if st.button('generate resume'):
  with st.spinner("running agent"):

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

    st.divider()
    response = agent.invoke({'messages':[{'role': 'user', 'content':job_prompt}]}) 

    job_code = response['messages'][-1].content[-1]['text']
    st.html(job_code , width="stretch" , unsafe_allow_javascript=True)




