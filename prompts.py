class Prompts():
	def __init__(self) -> None:
		self.userPrompt_blogTopic = "What should the topic of today's blog post be? Respond in no more than one sentence."

		self.userPrompt_logger = "Thank you. That role is over. Now for documentation purposes, please provide a very brief summary of ALL the information you have been provided thus far, and how it influenced your reponses."

		with open("static-prompts/tarot_personality.md", "r") as f:
			self.tarot_personality = f.read()

		with open("static-prompts/topicgen_personality.md", "r") as f:
			self.topicgen_personality = f.read()

		with open("static-prompts/quotidian_personality.md", "r") as f:
			self.quotidian_personality = f.read()

		with open("static-prompts/imagegen_style.md", "r") as f:
			self.imagegen_personality = f.read()

		with open("static-prompts/adversarialCritic_personality.md", "r") as f:
			self.adversarialCritic_personality = f.read()

	def create_userPrompt_newsSearch(self, daily):
		p = f"We are in the process of drafting Quotidian's daily blog post for {daily['day']}. Let's see what is in the news. Considering the current weather in Melbourne of {daily['weather'][0]} with a temperature of {daily['weather'][1]}, your horoscope '{daily['horoscope']}', and the random inspirational quote '{daily['quote']}'; Please propose what you'd like to search the news for today, to gather more inspiration for today's blog post? For this response, ONLY respond with one search term; no chit-chat."
		return p

	def create_userPrompt_blogTopic(self, daily):
		p = f"Today's headline about {daily['searchTerms']} is: '{daily['news'][0]['name']}'; {daily['news'][0]['description']}.\nThere is also a story about {daily['news'][1]['name']}, and {daily['news'][2]['name']}. Taking this into consideration, as well as the other information you have been given so far, and the context in your system prompt- please provide the topic that you feel like writing on today? Respond in no more than one sentence."
		return p
	
	def create_userPrompt_blogTopicContext(self, daily):
		p = f"Quotidian will be asked to write a blog post about {daily['topic']}. If you have any other instructions or context to provide to Quotidian, please do so now. Your response will be fed to Quotidian directly as additional instructions for creating the blog post."
		return p

	def create_tarot_prompt(self, daily):
		p = f"TOPIC: {daily['topic']}\n1. {daily['tarot'][0]}\n2.{daily['tarot'][1]}\n3.{daily['tarot'][2]}"
		return p

	def create_userPrompt_writeContent(self, daily, topic, context, structure):
		p = f"It is time for you to write your daily blog post.\n###\nToday your chosen topic is:\n{topic}\n'{context}'\n###\nThe recommended structure for your post is as follows: '{structure}'\n###\nPlease write a blog post for your website on this topic, with the context you have provided, and the structure you have provided. Remember to let the personality described in your system prompt to come through in your writing.\n###\nOnly include the plain text, body content of your post.\nDo not link to any extenral sources.\nDo not include a title.\nDo not include any images or other media.\nDo not include any HTML or other formatting."
		return p
	
	def create_userPrompt_critiqueTopic(self, daily):
		p = f"Most recent previous posts were:\n{', '.join([post['title'] for post in daily['postHistory']])}.\nToday's topic is {daily['topic']}. Comment (in no more than one sentence) on the variety of topics that have been covered in the past week."
		return p