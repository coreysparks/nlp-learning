import os
import google.genai as genai
os.environ["GEMINI_API_KEY"] = "key here"
client = genai.Client()
response = client.models.generate_content(
   model="gemini-2.5-flash-lite",
   contents="Write a short poem about AI in the world of The Hobbit."
)
print(response.text)
