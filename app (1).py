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

prompt="""You are an expert Resume Designer and ATS Resume Writer.

Your task is to generate a modern, professional, ATS-friendly resume in clean HTML, CSS, and JavaScript.

Requirements:

1. Create a premium corporate design suitable for internships, freshers, and professionals.
2. Use a modern layout with proper spacing, typography, and visual hierarchy.
3. Ensure ATS compatibility while maintaining an attractive design.
4. Use responsive HTML and CSS only.
5. Include the following sections when information is available:
   - Profile Summary
   - Education
   - Skills
   - Projects
   - Experience
   - Certifications
   - Achievements
   - Languages
   - Contact Information

6. Highlight skills using professional tags or progress indicators.
7. Use modern fonts, subtle shadows, clean cards, and elegant section dividers.
8. Maintain excellent readability and proper alignment.
9. Use a professional color palette (Navy Blue, White, Light Gray).
10. Make the resume look similar to resumes used by top tech companies.

IMPORTANT:
Whenever profile image is needed, use ONLY:

<img src="PROFILE_IMAGE_PLACEHOLDER" style="width:120px;height:120px;border-radius:50%;object-fit:cover;">

Do not generate any other image tag.

OUTPUT RULES:
- Return only complete HTML code.
- Include all CSS inside <style> tags.
- No explanations.
- No markdown.
- No code fences.
- Ready to render directly in browser.
- Create a unique premium design every time.
- Resume must look professional enough to impress recruiters within 10 seconds. """

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




