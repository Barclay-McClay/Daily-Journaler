import os, requests
from openai import OpenAI # AzureOpenAI
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from prompts import Prompts

class Brain():
    def __init__(self):
        print(f"---+---+---+---+---+---+---+---\nCreating new neural anatomy instance\n---+---+---+---+---+---+---+---")
        self.in_flow = True # Switches to False at end of init
        self.flow_interrupt = False
        # Openai
        self.openaiClient=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.deployment_name=os.getenv("AZURE_OPENAI_MODEL")
        self.temperature = 1
        self.maxTokens = 800
        self.current_system_prompt = ""
        self.allPrompts = Prompts()
        self.conversation = [
            {
                "role": "system",
                        "content": self.current_system_prompt
            }
        ]
        # Temporal
        self.datetime = datetime
        #----------------------------------------------

##################################################################################################################################
#                                       ONLY ALTER CODE ENCLOSED BY THE HASHES
# This is to ensure compatiblity when this is integrated into golem cyberdeck. We will be adding the functions in here to the golem's neural anatomy class.

    def action_journal(self):
        # Gather today's details
        weather_pack = self.action_get_weather()
        news_pack = self.action_get_news()
        horoscope = self.action_get_horoscope()
        # backup settings
        max_token_backup = self.maxTokens
        conv_backup = self.conversation
        # Create conversation to post
        # Get topic
        self.conversation = [
            {
                "role": "system",
                "content": self.allPrompts.create_journal_topic(weather_pack,news_pack,horoscope)
            },
            {
                "role": "user",
                "content": "What should the topic of today's blog post be? Respond in no more than one sentence."
            }
        ]
        topic = self.post()
        self.log_action(f"Today's journal topic: {topic}")
        # Get blog post
        self.maxTokens = 2000
        self.conversation = [
            {
                "role": "system",
                "content": self.allPrompts.create_journal_prompt(weather_pack,news_pack,horoscope)
            },
            {
                "role": "user",
                "content": topic
            }
        ]
        response = self.post()
        # Output to html
        day = datetime.now().strftime("%Y-%m-%d")
        file_path = f"./journals/journal_{day}.html"
        with open(file_path, "w") as f:
            f.write(response)
        # Restore settings
        self.maxTokens = max_token_backup
        self.conversation = conv_backup
        return file_path



    def action_get_news(self):
        base_url = "https://api.bing.microsoft.com/v7.0/news"
        params = {
            "cc": "au",
            "category": "Entertainment",
            "count": 3,
            "freshness": "Day",
            "q": "technology",
            "mkt": "en-AU",
        }
        headers = { 'Ocp-Apim-Subscription-Key': os.getenv("AZURE_NEWS_KEY") }
        response = requests.get(base_url, headers=headers, params=params)
        news_data = response.json()
        pack = []
        for n in news_data["value"]:
            pack.append({"name": n["name"], "description": n["description"]})
            self.log_action(f"News headline: {n['name']}")
        return pack

    def action_get_horoscope(self, sign="aries"):
        base_url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?day=TODAY&sign={sign}"
        response = requests.get(base_url)
        data = response.json()["data"]
        horoscope = data["horoscope_data"]
        self.log_action(f"{sign} horoscope: {horoscope}")
        return horoscope

##################################################################################################################################
##################################################################################################################################


    def log_action(self,log_text):
        timestamp = self.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        todays_date = timestamp.split(" ")[0]
        txt = f"{timestamp} | {log_text}\n"
        print(txt)
        # append to log file
        with open(f"./logs/logs_{todays_date}.txt", "a") as log_file:
            log_file.write(txt)

    def action_get_weather(self, lat=-37.81176117471146, lon=144.96529753582274):
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "appid": os.getenv("OPENWEATHER_KEY"),
            "units": "metric"
        }
        response = requests.get(base_url, params=params)
        weather_data = response.json()
        data = [weather_data["weather"][0]["description"], str(weather_data["main"]["temp"]) + "°C"]
        self.log_action(f"Weather: {data[0]}, {data[1]}")
        return data

    def action_conversation_reset(self):
        self.conversation = [
            {
                "role": "system",
                "content": self.current_system_prompt
            }
        ]
        print("Conversation reset")

    def add_prompt(self,prompt):
        self.conversation.append({
            "role": "user",
            "content": prompt
        })

    def add_response(self,botReply):
        self.conversation.append({
            "role": "assistant",
            "content": botReply
        })

    def post(self):
        print("Posting")
        try:
            completion = self.openaiClient.chat.completions.create(
                model=self.deployment_name,
                messages = self.conversation,
                temperature=1,
                max_tokens=self.maxTokens,
                top_p=0.95,
                frequency_penalty=0.1,
                presence_penalty=0,
                )
            return completion.choices[0].message.content
        except Exception as err:
            print(err)
            return "I'm sorry, I've malfunctioned. Give me a moment, then try again."