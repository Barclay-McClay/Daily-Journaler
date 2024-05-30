# Daily Journaler
cd ~/Daily-Journaler/

# Run the blogger script to generate the blog post
python3 ./auto_blog.py

# Move the blog post to the blog directory
mv ./journals/* ~/quotidian/blog-posts/
mv ./blog-images/* ~/quotidian/blog-images/

# Now we head over to the blog directory and post our updates
cd ~/quotidian/

git config --global user.email $GITHUB_EMAIL
git config --global user.name $GITHUB_NAME

git remote set-url origin https://$GITHUB_TOKEN@github.com/$GITHUB_NAME/quotidian.git/

# Add all files to the git repository
git add .

datestamp=$(date -I)

# Commit the changes
git commit -m "Journal $datestamp"

# Push the changes to the remote repository
git push https://$GITHUB_NAME:$GITHUB_TOKEN@github.com/$GITHUB_NAME/quotidian.git/

# Exit the script