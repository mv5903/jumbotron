#!/bin/bash

# Define the path to your repository
REPO_DIR="/home/matt/jumbotron"

# Navigate to your repository directory
cd $REPO_DIR

# Fetch the latest commits from the remote repository
git fetch

# Get the hash of the latest commit in the remote repository
LATEST_REMOTE_COMMIT=$(git rev-parse origin/main)

# Get the hash of the latest commit in your local clone of the repository
LATEST_LOCAL_COMMIT=$(git rev-parse HEAD)

# Compare the commits
if [[ $LATEST_REMOTE_COMMIT != $LATEST_LOCAL_COMMIT ]]; then
    # Pull the latest code from the remote repository
    git pull
    
    # Restart the systemd service (this restarts the python script)
    sudo systemctl restart jumbotron.service
    
    # Optionally, log the action
    echo "$(date) - Jumbotron service restarted due to new commit $LATEST_REMOTE_COMMIT" >> /home/matt/jumbotron/auto-pull.log
fi
