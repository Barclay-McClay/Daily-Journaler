# Daily Journaler
cd ~/Daily-Journaler/

source ./.env

# Run the blogger script to generate the blog post
python3 ./auto_blog.py

# Move the blog post to the blog directory
mv ./blog-posts/* ~/quotidian/blog-posts/
mv ./blog-images/* ~/quotidian/blog-posts/blog-images/
cp ./blog-data.json ~/quotidian/blog-posts/

# Now we head over to the blog directory and post our updates to github
cd ~/quotidian/

git config --global user.email $GITHUB_EMAIL
git config --global user.name $GITHUB_NAME

git remote set-url origin https://$GITHUB_TOKEN@github.com/$GITHUB_NAME/quotidian.git/

git add .

datestamp=$(date -I)

git commit -m "Journal $datestamp"

git push https://$GITHUB_NAME:$GITHUB_TOKEN@github.com/$GITHUB_NAME/quotidian.git/

