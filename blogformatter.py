from datetime import datetime, timedelta

class BlogFormatter:
    def __init__(self):
        pass

    def action_generate_html(self, title, content, image_path, logger_summary, daily_data, topic_context, suggested_structure, post_feedback):
        day=datetime.now().strftime("%Y-%m-%d")
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
                <div class="post-details">
                    <details>
                        <summary>Take a peek behind the curtains...</summary>
                        <p id="creation-details">{logger_summary}</p>
                        <p><b>Today's horoscope:</b> {daily_data['horoscope']}</p>
                        <p><b>Today's quote:</b> <q>{daily_data['quote']}</q></p>
                        <p>Quotidian searched for news on <em>{daily_data['searchTerms']}</em>, and today's headlines were:</p>
                        <ul>
                            <li>{daily_data['news'][0]['name']}</li>
                            <li>{daily_data['news'][1]['name']}</li>
                            <li>{daily_data['news'][2]['name']}</li>
                        </ul>
                        <p><b>Quotidian used this data to arrive at the topic of:</b></p>
                        <p id="creation-details">{daily_data['topic']}</p>
                        <p id="creation-details">{topic_context}</p>
                        <p><b>Today's tarot cards:</b></p>
                        <ul>
                            <li>{daily_data['tarot'][0]}</li>
                            <li>{daily_data['tarot'][1]}</li>
                            <li>{daily_data['tarot'][2]}</li>
                        </ul>
                        <p><b>Quotidian used the tarot cards to structure the blog post as follows:</b></p>
                        <p  id="creation-details">{suggested_structure}</p>
                        <p><b>Feedback from the adversarial critic:</b></p>
                        <p id="creation-details">{post_feedback[0]}</p>
                        <p id="creation-details">{post_feedback[1]}</p>
                    </details>
                </div>
                <div class="post-navigation">
                    <a href="./{prev_post_url}" class="nav-prev">Previous Post</a>
                    <a href="../index.html" class="bottom-backlink">Back to Home</a>
                    <a href="./index.html" class="bottom-backlink">Blog Index</a>
                    <a href="./{next_post_url}" class="nav-next">Next Post</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def action_generate_manualBlog(self, title, content, image_path, logger_summary, post_feedback):
        day=datetime.now().strftime("%Y-%m-%d")
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
                    <h2 class="post-title-devblog">{title}</h2>
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
                <div class="post-details">
                    <details>
                        <summary>Take a peek behind the curtains...</summary>
                        <p><b>Quotidian's response to the above:</b></p>
                        <p id="creation-details">{logger_summary}</p>
                        <p><b>Adversarial critic's brutal opinion:</b></p>
                        <p id="creation-details">{post_feedback}</p>
                    </details>
                </div>
                <div class="post-navigation">
                    <a href="./{prev_post_url}" class="nav-prev">Previous Post</a>
                    <a href="../index.html" class="bottom-backlink">Back to Home</a>
                    <a href="./index.html" class="bottom-backlink">Blog Index</a>
                    <a href="./{next_post_url}" class="nav-next">Next Post</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
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