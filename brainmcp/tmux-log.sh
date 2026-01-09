#!/bin/bash
SESSION_NAME=${1:-default}
LOG_DIR="$HOME/tmux_logs"
mkdir -p "$LOG_DIR"

tmux new-session -d -s "$SESSION_NAME"
tmux pipe-pane -o "cat >> $LOG_DIR/${SESSION_NAME}.log"
tmux attach-session -t "$SESSION_NAME"
