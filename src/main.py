import gui
from dotenv import load_dotenv
import os

#import random
#import time
#import pandas as pd
#app = gui.App()


load_dotenv()

import google.generativeai as genai

api_key = os.getenv("API_KEY")

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