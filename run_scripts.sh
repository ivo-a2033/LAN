#!/bin/bash

# Command to run Python script (replace with your actual script and arguments)
python_command1="py server.py"
python_command2="py client.py"
python_command3="py client2.py"

# Run the Python script in separate Bash sessions
start bash -l -c "$python_command1"
start bash -l -c "$python_command2"
start bash -l -c "$python_command3"