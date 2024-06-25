import argparse
from Brain import Brain

# Define argument parser and arguments
parser = argparse.ArgumentParser()
parser.add_argument('-title', type=str, required=True)
parser.add_argument('-file', type=str, required=True)
args = parser.parse_args()

# Get values from arguments
post_title = args.title
content_filepath = args.file

bot = Brain()
path = bot.start_flow_manualBlog(post_title, content_filepath)
print(f"Blog post written to: {path}")