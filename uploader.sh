# Daily Journaler
cd /home/bitnami/Daily-Journaler/

python3 ./auto_blog.py

source ./.env

git config --global user.email $GITHUB_EMAIL
git config --global user.name $GITHUB_NAME

git remote set-url origin https://$GITHUB_TOKEN@github.com/$GITHUB_NAME/Daily-Journaler.git/

# Add all files to the git repository
git add .

datestamp=$(date -I)

# Commit the changes
git commit -m "Journal $datestamp"

# Push the changes to the remote repository
git push https://$GITHUB_NAME:$GITHUB_TOKEN@github.com/$GITHUB_NAME/Daily-Journaler.git/

# Exit the script
