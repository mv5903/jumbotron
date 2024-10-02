#!/bin/bash

# Start a new tmux session named 'dev_session'
tmux new-session -d -s dev_session

# Split the window vertically
tmux split-window -h

# Run the React dev server in the left pane (pane 0)
tmux send-keys -t dev_session:0.0 'npm run --prefix frontend/jumbotron dev' Enter

# Run the Flask server in the right pane (pane 1)
tmux send-keys -t dev_session:0.1 'python3 backend/api.py' Enter

# Attach to the tmux session
tmux attach -t dev_session
