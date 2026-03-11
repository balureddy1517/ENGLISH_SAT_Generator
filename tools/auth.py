from dotenv import load_dotenv
from openai import OpenAI
import os


load_dotenv()

client = OpenAI(api_key=os.getenv(".env/OPENAI_API_KEY"))