#!/bin/bash

# This script ensures that the feed reader runs with the correct pyenv environment

# Load pyenv if it's not already in the PATH
if [ -z "$(which pyenv)" ]; then
  export PYENV_ROOT="$HOME/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init --path)"
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"
fi

# Activate the feed-reader environment
export PYENV_VERSION=feed-reader

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the feed reader script with all arguments passed to this wrapper
"$SCRIPT_DIR/feed_reader.py" "$@"

# Exit with the same status as the Python script
exit $?
