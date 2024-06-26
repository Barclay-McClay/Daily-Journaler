import os, requests, json, random
from openai import OpenAI # AzureOpenAI
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

from prompts import Prompts
from blogformatter import BlogFormatter

class Brain():
    def __init__(self):
        print(f"---+---+---+---+---+---+---+---\nCreating new neural anatomy instance\n---+---+---+---+---+---+---+---")
        # Openai
        self.openaiClient=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.deployment_name=os.getenv("AZURE_OPENAI_MODEL")
        self.temperature = 1
        self.maxTokens = 2000
        self.allPrompts = Prompts()
        self.current_system_prompt = self.allPrompts.quotidian_personality
        self.conversation = [
            {
                "role": "system",
                        "content": self.current_system_prompt
            }
        ]
        # Temporal
        self.datetime = datetime
        #----------------------------------------------
        self.formatter = BlogFormatter()

    def start_flow_manualBlog(self, post_title, content_filepath):
        # This flow is for manually creating "Developer's notes" style blog post. Not written by AI.
        day = datetime.now().strftime("%Y-%m-%d")
        self.log_action(f"Mannual blog post: {post_title}")
        # Get the text from the file
        with open(content_filepath, "r") as f:
            bodycontent_repsonse = f.read()
        # Quotidian's read
        self.action_conversation_reset(self.allPrompts.quotidian_personality)
        self.add_prompt(self.allPrompts.userPrompt_readManualBlog + f"\n\n{bodycontent_repsonse}")
        logger_summary = self.post()
        # Get some feedback on the post from the adversarial critic
        self.action_conversation_reset(self.allPrompts.adversarialCritic_personality)
        self.add_prompt(f"Please provide your feedback on the blog post:\n{post_title}\n{bodycontent_repsonse}")
        post_feedback = self.post()
        self.log_action(f"Adversarial critic feedback: {post_feedback}")
        # -----------------------------------------------------------
        # Format it as HTML
        file_path = f"./blog-posts/devBlog_{day}.html"
        image_path = f"./blog-images/image_devBlog_{day}.png"
        # Get the first scentence of the post
        blogpost_preview = bodycontent_repsonse[:100] + "..."
        # Format the blog post as HTML
        html_response = self.formatter.action_generate_manualBlog(post_title, bodycontent_repsonse, image_path, logger_summary, post_feedback)
        # Generate and save an image to go with the post
        image_url = self.action_get_image_url(post_title, self.allPrompts.imagegen_manualPost_personality)
        self.action_save_image(image_url, image_path)
        # Update the blog index
        self.action_update_blog_index(post_title, day, blogpost_preview, "devBlog")
        # Write out the blog post's html as a file
        with open(file_path, "w") as f:
            f.write(html_response)
        return file_path

    #----------------------------------------------------------------------------------------------------------------------------------
    # This is the main 'pipeline' that causes the bot to create and save the blog post
    #----------------------------------------------------------------------------------------------------------------------------------
    def start_flow_writeBlog(self, dev_mode=False):
        if dev_mode: # Just for logging purposes
            self.log_action("------DEV MODE IS ON------")

        # First, we'll gather the data about today that comes from external APIs
        day = datetime.now().strftime("%Y-%m-%d")
        self.daily_data = {
            'day': day,
            'weather': self.action_get_weather(),
            'horoscope': self.action_get_horoscope(),
            'quote': self.action_get_quote(),
            'tarot': self.action_get_tarot(3),
            'topic': '', # We'll generate a topic
            'searchTerms': '', # Quotidian will provide us with search terms
            'news': '', # We'll search for the news using provided search terms
            'postHistory': self.action_get_lastFivePosts()
        }
        # Start Pipeline Enrichment process-----------------------------------
        # [0] RESET - Topicgen personality to system prompt
        self.action_conversation_reset(self.allPrompts.topicgen_personality)
        # [1] First prompt: Given the weather, horoscope, quote, etc. What should we search the news for today?
        self.add_prompt(self.allPrompts.create_userPrompt_newsSearch(self.daily_data))
        self.daily_data['searchTerms'] = self.post()
        self.add_response(self.daily_data['searchTerms'])
        # We've got the search terms stored in our daily_data, now we can search for news headlines
        self.daily_data['news'] = self.action_get_news(self.daily_data['searchTerms'])
        # [2] Second Prompt: Given the news headlines, what should we write about today?
        self.add_prompt(self.allPrompts.create_userPrompt_blogTopic(self.daily_data))
        topic = self.post()
        self.daily_data['topic'] = topic
        self.add_response(topic)
        self.log_action(f"Today's journal topic: {topic}")
        # [3] Third Prompt: Given the topic, anything more to add?
        self.add_prompt(self.allPrompts.create_userPrompt_blogTopicContext(self.daily_data))
        topic_context = self.post()
        self.log_action(f"More context: {topic_context}")
        self.add_prompt(self.allPrompts.userPrompt_logger)
        logger_summary = self.post()
        self.log_action(f"Logger summary: {logger_summary}")
        # [4] RESET - Tarot personality to system prompt
        self.action_conversation_reset(self.allPrompts.tarot_personality)
        # [5] First Prompt: Given the tarot cards, how should we structure the blog post?
        self.add_prompt(self.allPrompts.create_tarot_prompt(self.daily_data))
        suggested_structure_raw = self.post()
        # I REALLY don't want the bot to talk about the tarot, so I'm going to make extra sure it doesn't leak into the prompts
        suggested_structure = suggested_structure_raw.replace("tarot", "")
        suggested_structure = suggested_structure_raw.replace("Tarot", "")
        suggested_structure = suggested_structure_raw.replace(self.daily_data['tarot'][0], "")
        suggested_structure = suggested_structure_raw.replace(self.daily_data['tarot'][1], "")
        suggested_structure = suggested_structure_raw.replace(self.daily_data['tarot'][2], "")
        self.log_action(f"Tarot-based structure: {self.daily_data['tarot']}, {suggested_structure}")
        # [6] RESET - Quotidian personality to system prompt
        self.action_conversation_reset(self.allPrompts.quotidian_personality)
        # [7] First Prompt: Construct the body content for the post
        self.add_prompt(self.allPrompts.create_userPrompt_writeContent(self.daily_data, topic, topic_context, suggested_structure))
        bodycontent_repsonse = self.post()
        self.add_response(bodycontent_repsonse)
        # [8] Second Prompt: Given the body content, what should the title be?
        self.add_prompt("What should the title of this blog post be? Respond with only the title. Do not make it a two-part title, only include one simple and clear, few-words headline")
        titlecontent_response = self.post()
        # sanitise the title, only alphanumeric characters, spaces, dashes and colons allowed
        titlecontent_response = ''.join(e for e in titlecontent_response if e.isalnum() or e.isspace() or e == "-" or e == ":")
        titlecontent_response = titlecontent_response.strip()
        self.add_response(titlecontent_response)
        # Let's get the adverserial critic to give us some feedback on the post
        # [9] RESET - Adversarial Critic personality to system prompt
        self.action_conversation_reset(self.allPrompts.adversarialCritic_personality)
        # [10] First Prompt: Look at the topics
        self.add_prompt(self.allPrompts.create_userPrompt_critiqueTopic(self.daily_data))
        post_feedback = [self.post()]
        self.add_response(post_feedback[0])
        # [11] Second Prompt: Given the blog post, what feedback do you have for the author?
        self.add_prompt(f"Please provide your feedback on the blog post:\n{titlecontent_response}\n{bodycontent_repsonse}")
        post_feedback.append(self.post())
        self.add_response(post_feedback[1])
        self.log_action(f"Adversarial critic feedback: {post_feedback}")
        # -----------------------------------------------------------
        # Dev Mode will save the response as a markdown file and end the function here -----
        if dev_mode:
            print(titlecontent_response)
            print(bodycontent_repsonse)
            print(f"-----")
            print(logger_summary)
            print(f"-----")
            print(post_feedback)
            file_path = f"./blog-posts/journal_{day}_dev.md"
            # Write out the blog post's html as a file
            with open(file_path, "w") as f:
                f.write(f"# {titlecontent_response}\n\n{bodycontent_repsonse}\n\n## Behind the scenes\n{logger_summary}\n\n## Adversarial critic feedback\n{post_feedback[0]}\n{post_feedback[1]}")
            self.log_action(f"----- COMPLETING DEV MODE FLOW ------")
            return file_path
        # -----------------------------------------------------------
        # [X] End Pipeline Enrichment process-----------------------------------
        # Now we have the blog post, we can save it as a file
        file_path = f"./blog-posts/journal_{day}.html"
        image_path = f"./blog-images/image_journal_{day}.png"
        # Get the first scentence of the post
        blogpost_preview = bodycontent_repsonse[:100] + "..."
        # Update the blog index
        self.action_update_blog_index(titlecontent_response, day, blogpost_preview, "journal")

        # Format the blog post as HTML
        html_response = self.formatter.action_generate_html(titlecontent_response, bodycontent_repsonse, image_path, logger_summary, self.daily_data, topic_context, suggested_structure_raw, post_feedback)
        # Generate and save an image to go with the post
        image_url = self.action_get_image_url(topic)
        self.action_save_image(image_url, image_path)

        # Write out the blog post's html as a file
        with open(file_path, "w") as f:
            f.write(html_response)
        return file_path
        # ----------------------------------------------------------------------------------------------------------------------------------
        # End of main 'pipeline' The blog post has been generated, saved, and the blog index updated
        # ----------------------------------------------------------------------------------------------------------------------------------


    def action_get_tarot(self,count=1):
        major_arcana = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", 
                        "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", 
                        "The Star", "The Moon", "The Sun", "Judgement", "The World"]
        minor_arcana = []
        suits = ["Wands", "Cups", "Swords", "Pentacles"]
        ranks = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", 
                "Ten", "Page", "Knight", "Queen", "King"]
        for suit in suits:
            for rank in ranks:
                minor_arcana.append(f"{rank} of {suit}")
        tarot_deck = major_arcana + minor_arcana
        return random.sample(tarot_deck, count)

    def action_get_news(self,searchTerms=""):
        count = 3
        pack = []
        self.log_action(f"Searching news: {searchTerms}")
        base_url = "https://api.bing.microsoft.com/v7.0/news"
        params = {
            "cc": "au",
            "count": count,
            "freshness": "Day",
            "q": searchTerms,
            "mkt": "en-AU",
        }
        headers = { 'Ocp-Apim-Subscription-Key': os.getenv("AZURE_NEWS_KEY") }
        response = requests.get(base_url, headers=headers, params=params)
        news_data = response.json()
        if response.status_code != 200:
            self.log_action(f"Error: {news_data['error']['message']}")
            for n in range(count):
                pack.append({"name": "Error", "description": 'There was an error fetching the news.'})
        for n in news_data["value"]:
            pack.append({"name": n["name"], "description": n["description"]})
            self.log_action(f"News headline: {n['name']}")
        return pack

    def action_get_horoscope(self, sign="aries"):
        base_url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?day=TODAY&sign={sign}"
        response = requests.get(base_url)
        if response.status_code != 200:
            self.log_action(f"Error Horoscope: {response.json()['error']}")
            return "Error"
        data = response.json()["data"]
        horoscope = data["horoscope_data"]
        self.log_action(f"Horoscope: {horoscope}")
        return horoscope
    
    def action_get_quote(self):
        base_url = "https://zenquotes.io/api/random"
        response = requests.get(base_url)
        quote_data = response.json()
        if response.status_code != 200:
            self.log_action(f"Error Quote: {quote_data['error']}")
            return "Error"
        quote = f"{quote_data[0]['q']} - {quote_data[0]['a']}"
        self.log_action(f"Quote: {quote}")
        return quote
    
    def action_get_image_url(self, prompt="", personality = ""):
        if prompt != "":
            if personality == "":
                personality = self.allPrompts.imagegen_personality # Default if none selected
            response = self.openaiClient.images.generate(
                prompt=prompt + "\n" + personality,
                model="dall-e-3",
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            self.log_action(f"Image generated: {image_url}")
            return image_url
        else:
            return None
        
    def action_save_image(self, image_url, path):
        with open(path, "wb") as f:
            f.write(requests.get(image_url).content)
        self.log_action(f"Image saved: {path}")
        return path

    def action_get_lastFivePosts(self):
        with open('./blog-data.json', 'r') as f:
            posts = json.load(f)
        return posts['posts'][-5:]

    def action_update_blog_index(self, blogpost_title, blogpost_date, blogpost_preview, blogpost_type="journal"):
        # Assuming posts is a list of your existing posts
        with open('./blog-data.json', 'r') as f:
            posts = json.load(f)
        # Append the new post to the list
        posts['posts'].append({
            'title': blogpost_title,
            'date': blogpost_date,
            'url': f'blog-posts/{blogpost_type}_{blogpost_date}.html',
            'image': f'image_{blogpost_type}_{blogpost_date}.png',
            'preview': blogpost_preview,  # You'll need to generate this from the post content
            'postType': blogpost_type
        })
        # Write the updated list back to the file
        with open('./blog-data.json', 'w') as f:
            json.dump(posts, f)

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
        try:
            if response.status_code != 200:
                self.log_action(f"Error: {response.json()}")
                return ["Error", "Error"]
            weather_data = response.json()
            data = [weather_data["weather"][0]["description"], str(weather_data["main"]["temp"]) + "°C"]
            self.log_action(f"Weather: {data[0]}, {data[1]}")
            return data
        except Exception as e:
            self.log_action(f"Error getting weather: {e}")
            return ["Error", "Error"]

    def action_conversation_reset(self,sysprompt=""):
        if sysprompt == "":
            sysprompt = self.current_system_prompt
        self.current_system_prompt = sysprompt
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