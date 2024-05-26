# This script is run once every-day on a server to commit changes to a git repository
# The script is run using a cron job

# Change to the directory where the files are stored
cd ~/path/to/directory

# Add all files to the git repository
git add .

# Commit the changes
git commit -m "Daily update"

# Push the changes to the remote repository
git push origin master

# Exit the script