from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Try the stable Gemini 1.5 Flash model instead
response = client.models.generate_content(
    model='gemini-2.5-flash',  # More stable model
    contents='Say hello!'
)

print(response.text)