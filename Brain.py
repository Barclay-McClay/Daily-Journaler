import os, requests, json, random
from openai import OpenAI # AzureOpenAI
from datetime import datetime, timedelta
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
            'news': '' # We'll search for the news using provided search terms
        }
        # Generate some metadata to save the file
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
        # [4] RESET - Tarot personality to system prompt
        self.action_conversation_reset(self.allPrompts.tarot_personality)
        # [5] First Prompt: Given the tarot cards, how should we structure the blog post?
        self.add_prompt(self.allPrompts.create_tarot_prompt(self.daily_data))
        suggested_structure = self.post()
        # I REALLY don't want the bot to talk about the tarot, so I'm going to make extra sure it doesn't leak into the prompts
        suggested_structure = suggested_structure.replace("tarot", "")
        suggested_structure = suggested_structure.replace("Tarot", "")
        suggested_structure = suggested_structure.replace(self.daily_data['tarot'][0], "")
        suggested_structure = suggested_structure.replace(self.daily_data['tarot'][1], "")
        suggested_structure = suggested_structure.replace(self.daily_data['tarot'][2], "")
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
        # Dev Mode will save the response as a markdown file and end the function here -----
        if dev_mode:
            file_path = f"./blog-posts/journal_{day}_dev.md"
            # Write out the blog post's html as a file
            with open(file_path, "w") as f:
                f.write(f"# {titlecontent_response}\n\n{bodycontent_repsonse}")
            self.log_action(f"----- COMPLETING DEV MODE FLOW ------")
            return file_path
        # -----------------------------------------------------------
        # [X] End Pipeline Enrichment process-----------------------------------
        # Now we have the blog post, we can save it as a file
        file_path = f"./blog-posts/journal_{day}.html"
        image_path = f"./blog-images/image_{day}.png"
        # Get the first scentence of the post
        blogpost_preview = bodycontent_repsonse[:100] + "..."
        # Update the blog index
        self.action_update_blog_index(titlecontent_response, day, blogpost_preview)

        # Format the blog post as HTML
        html_response = self.action_generate_html(titlecontent_response, bodycontent_repsonse, image_path)
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

    def action_format_htmlbody(self,content):
        # Split content into paragraphs at every newline
        html_paragraphs = []
        paragraphs = content.split("\n")
        # Wrap each paragraph in <p> tags
        for p in paragraphs:
            if p.strip():
                p = f"<p>{p}</p>"
            else:
                p = "<br>"
            html_paragraphs.append(p)
        return "\n".join(html_paragraphs)
    
    def action_generate_html(self, title, content, image_path):
        day=self.daily_data['day']
        tomorrow=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        # Initialize previous and next URLs
        prev_post_url = f"journal_{yesterday}.html"
        next_post_url = f"journal_{tomorrow}.html"
        # Next and previous links
        content = self.action_format_htmlbody(content)
         # Construct relative paths based on the date
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <head>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Quotidian's Journal | {title}</title>
            <link rel="stylesheet" href="./blog-style.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <a href="../index.html" class="header-backlink">Back to Home</a>
                    <h2 class="post-title">{title}</h2>
                    <p class="post-date">{day}</p>
                </header>
                <div class="grid-container">
                    <div class="grid-item">
                        <img src="{image_path}" class="blog-img" />
                    </div>
                    <div class="blog-bodycontent">
                        {content}
                    </div>
                </div>
                <div class="post-navigation">
                    <a href="../{prev_post_url}" class="nav-prev">Previous Post</a>
                    <a href="../index.html" class="bottom-backlink">Back to Home</a>
                    <a href="../{next_post_url}" class="nav-next">Next Post</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html

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
        self.log_action(f"Searching news: {searchTerms}")
        base_url = "https://api.bing.microsoft.com/v7.0/news"
        params = {
            "cc": "au",
            "count": 3,
            "freshness": "Day",
            "q": searchTerms,
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
        self.log_action(f"Horoscope: {horoscope}")
        return horoscope
    
    def action_get_quote(self):
        base_url = "https://zenquotes.io/api/random"
        response = requests.get(base_url)
        quote_data = response.json()
        quote = f"{quote_data[0]['q']} - {quote_data[0]['a']}"
        self.log_action(f"Quote: {quote}")
        return quote
    
    def action_get_image_url(self, prompt=""):
        if prompt != "":
            response = self.openaiClient.images.generate(
                prompt=prompt + "\n" + self.allPrompts.imagegen_personality,
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

    def action_update_blog_index(self, blogpost_title, blogpost_date, blogpost_preview):
        # Assuming posts is a list of your existing posts
        with open('./blog-data.json', 'r') as f:
            posts = json.load(f)
        # Append the new post to the list
        posts['posts'].append({
            'title': blogpost_title,
            'date': blogpost_date,
            'url': f'blog-posts/journal_{blogpost_date}.html',
            'image': f'image_{blogpost_date}.png',
            'preview': blogpost_preview  # You'll need to generate this from the post content
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
        weather_data = response.json()
        data = [weather_data["weather"][0]["description"], str(weather_data["main"]["temp"]) + "°C"]
        self.log_action(f"Weather: {data[0]}, {data[1]}")
        return data

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