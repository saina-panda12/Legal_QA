# # import google.generativeai as genai
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
# import os


# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# # genai.configure(api_key=GEMINI_API_KEY)
# # model = genai.GenerativeModel("gemini-1.5-flash")
# # # response = model2.generate_content("who are you")
# # # print(response.text)


# def get_llm_model():
#     return ChatGoogleGenerativeAI(
#         model='gemini-2.0-flash', 
#         api_key=GEMINI_API_KEY, 
#         temperature=0.0
#     )
# model = get_llm_model()


# from langchain_google_vertexai import VertexAI

# # Set  project details
# PROJECT_ID = "x-cycling-459817-i5"
# LOCATION = "us-central1"
# FINE_TUNED_MODEL_ID = "projects/x-cycling-459817-i5/locations/us-central1/endpoints/7423424223185469440" # This is the model ID from Vertex AI

# model = VertexAI(
#     model=FINE_TUNED_MODEL_ID,
#     temperature=0.5,
#     max_output_tokens=1024,
#     # top_p=0.95
# )
# def simple_query(prompt):
#     """Simple text generation"""
#     response = model.invoke("You are a legal QA chatbot specialized in Indian legal system. Answer with most interactive way. If question is not related to legal system then give a proper denial answer. "+prompt)
#     return response

# print("Simple query response:", simple_query("Hi, good morning!"))

from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()
#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Create a LangChain-compatible Gemini model instance
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key="AIzaSyCogIuJiuKH4G-MmGv5SeABlH2e3mV3czk",
    temperature=0.7  # optional: controls randomness
)