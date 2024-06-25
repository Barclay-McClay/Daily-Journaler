# Manual journal entry
cd ~/Daily-Journaler/

source ./.env

# Run the blogger script to generate the blog post
python3 ./dev_blog.py -title "$1" -file "$2"

# Move the blog post to the blog directory
mv ./blog-posts/* ~/quotidian/blog-posts/
mv ./blog-images/* ~/quotidian/blog-posts/blog-images/
cp ./blog-data.json ~/quotidian/blog-posts/

# Instead of pushing the post automatically, I'll make any last-minute edits (add links, formatting etc) and push manually

#cd ~/quotidian/
#git config --global user.email $GITHUB_EMAIL
#git config --global user.name $GITHUB_NAME
#git remote set-url origin https://$GITHUB_TOKEN@github.com/$GITHUB_NAME/quotidian.git/
#git add .
#datestamp=$(date -I)
#git commit -m "Dev Post $datestamp"
#git push https://$GITHUB_NAME:$GITHUB_TOKEN@github.com/$GITHUB_NAME/quotidian.git/

