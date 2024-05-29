from Brain import Brain

bot = Brain()
path = bot.start_flow_writeBlog()
print(f"Blog post written to: {path}")