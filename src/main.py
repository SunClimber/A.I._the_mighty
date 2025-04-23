import gui
from dotenv import load_dotenv
import os
import requests

#import random
#import time
#import pandas as pd
#app = gui.App()


load_dotenv()

import google.generativeai as genai

api_key = os.getenv("API_KEY")

#user input
user_search = input("please input an author to search for a list of his books available on Project Gutenberg: ")


response = requests.get(f"https://gutendex.com/books?search={user_search}")


data = response.json()

results = data["results"]



for book in results:
    print(book["title"])

#print(data["results"][0]["title"])

#set API using api-key
genai.configure(api_key= api_key)
while True:   
    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")

    #grab user input
    print("enter in prompt you bastard: ", end="")
    user_input = input()

    #generate response
    response = model.generate_content(user_input)

    print(response.text)



#app.mainloop()