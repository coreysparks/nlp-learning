import os
import google.genai as genai
os.environ["GEMINI_API_KEY"] = "AIzaSyDjwI7mgWT4LxwMGK7-eS79z95XtVtKj-c"
client = genai.Client()
response = client.models.generate_content(
   model="gemini-2.5-flash-lite",
   contents="Write a short poem about AI in the world of The Hobbit."
)
print(response.text)
