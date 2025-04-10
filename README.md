# feed-recorder
A simple Atom/RSS feed recorder written in Python

# Setting Up the Feed Reader with Cron

This guide explains how to set up the feed reader script to run automatically every day using cron on your Debian machine.

## Prerequisites

Make sure you have installed all required Python packages:

```bash
sudo apt update
sudo apt install python3-pip python3-yaml
pip3 install feedparser pyyaml
```

## Step 1: Prepare the Scripts and Configuration

1. Save the `feed_reader.py` script to your home directory or a location of your choice:
   ```bash
   mkdir -p ~/scripts
   # Copy the feed_reader.py to ~/scripts/feed_reader.py
   chmod +x ~/scripts/feed_reader.py
   ```

2. Create the YAML configuration file:
   ```bash
   # Copy the feed_config.yaml to ~/feed_config.yaml
   ```

## Step 2: Test the Script Manually

Before setting up cron, test the script manually to make sure it works:

```bash
# Run with default config and output locations
~/scripts/feed_reader.py

# Or specify custom paths
~/scripts/feed_reader.py --config ~/feed_config.yaml --output ~/feed_data.json
```

## Step 3: Set Up the Cron Job

1. Open your crontab file for editing:
   ```bash
   crontab -e
   ```

2. Add the following line to run the script every day at 10:00 AM:
   ```
   0 10 * * * ~/scripts/feed_reader.py --config ~/feed_config.yaml --output ~/feed_data.json
   ```

   If you want to suppress email notifications about the job, add `>/dev/null 2>&1` at the end:
   ```
   0 10 * * * ~/scripts/feed_reader.py --config ~/feed_config.yaml --output ~/feed_data.json >/dev/null 2>&1
   ```

3. Save and exit the editor.

## Step 4: Verify Your Cron Job

To verify that your cron job has been set up correctly:

```bash
crontab -l
```

## Logging

The script logs its activities to `~/feed_reader.log`. You can check this file to monitor the script's operation:

```bash
tail -f ~/feed_reader.log
```

## Changing Output Format

To save the data as CSV instead of JSON, simply change the output file extension:

```bash
~/scripts/feed_reader.py --output ~/feed_data.csv
```

And update your cron job accordingly.

## Troubleshooting

If the cron job isn't running:

1. Make sure the script is executable: `chmod +x ~/scripts/feed_reader.py`
2. Check the script path in the cron job is correct
3. Ensure the shebang line at the top of the script points to a valid Python interpreter
4. Check the log file for errors: `cat ~/feed_reader.log`

# Setting Up Feed Reader with pyenv

This guide explains how to set up the feed reader script to run with a specific Python environment managed by pyenv.

## Prerequisites

- pyenv already installed on your system
- Basic familiarity with pyenv commands

## Step 1: Create a Dedicated Python Environment

1. Install the desired Python version with pyenv (if not already installed):

   ```bash
   pyenv install 3.10.0  # Replace with your preferred version
   ```

2. Create a dedicated virtual environment for the feed reader:

   ```bash
   pyenv virtualenv 3.10.0 feed-reader  # Creates a virtual environment named 'feed-reader'
   ```

3. Verify the environment was created:

   ```bash
   pyenv virtualenvs  # Should list your new 'feed-reader' environment
   ```

## Step 2: Install Required Packages in the Environment

1. Activate the environment manually:

   ```bash
   pyenv activate feed-reader
   ```

2. Install the required packages:

   ```bash
   pip install feedparser pyyaml
   ```

3. Deactivate the environment when done:

   ```bash
   pyenv deactivate
   ```

## Step 3: Update the Script Shebang

1. Edit the feed_reader.py script to use the pyenv environment by replacing the first line:

   From:
   ```python
   #!/usr/bin/env python3
   ```

   To:
   ```python
   #!/usr/bin/env python
   ```

2. Make the script executable:

   ```bash
   chmod +x ~/scripts/feed_reader.py
   ```

## Step 4: Create a Wrapper Script

Create a wrapper script to ensure the correct environment is used:

1. Create a new file called `run_feed_reader.sh`:

   ```bash
   touch ~/scripts/run_feed_reader.sh
   chmod +x ~/scripts/run_feed_reader.sh
   ```

2. Add the following content to the file:

   ```bash
   #!/bin/bash

   # Path to the pyenv environment's Python interpreter
   export PYENV_VERSION=feed-reader

   # Run the feed reader script with any passed arguments
   ~/scripts/feed_reader.py "$@"
   ```

## Step 5: Set Up Local Directory Environment (Alternative Approach)

As an alternative to the wrapper script, you can use pyenv's local directory environment:

1. Navigate to your scripts directory:

   ```bash
   cd ~/scripts
   ```

2. Set the local Python environment:

   ```bash
   pyenv local feed-reader
   ```

3. This creates a `.python-version` file in the directory, which will tell pyenv to automatically use the feed-reader environment when running Python in this directory.

## Step 6: Setting Up Cron to Work with pyenv

When using cron, you need to ensure it has the full environment setup:

1. Open your crontab:

   ```bash
   crontab -e
   ```

2. Add the following to run the script at 10:00 AM daily using the wrapper script:

   ```
   0 10 * * * ~/scripts/run_feed_reader.sh --config ~/feed_config.yaml --output ~/feed_data.json
   ```

   Or, if using the full path to the pyenv Python interpreter:

   ```
   0 10 * * * PYENV_VERSION=feed-reader PYENV_ROOT="$HOME/.pyenv" PATH="$PYENV_ROOT/bin:$PATH" ~/scripts/feed_reader.py --config ~/feed_config.yaml --output ~/feed_data.json
   ```

## Testing Your Setup

Before relying on cron, test that the script runs correctly with your pyenv setup:

1. Run the wrapper script:
   ```bash
   ~/scripts/run_feed_reader.sh
   ```

2. Or run with the environment explicitly set:
   ```bash
   PYENV_VERSION=feed-reader ~/scripts/feed_reader.py
   ```

## Troubleshooting

- **Script can't find modules**: Ensure the modules are installed in the correct pyenv environment
- **Wrong Python version used**: Check that PYENV_VERSION is correctly set in your script or cron job
- **pyenv command not found in cron**: Make sure to include the full path to pyenv in your cron job
- **Check logs**: Review the feed_reader.log file for any errors

## Advantages of Using pyenv

- Isolated dependencies from your system Python
- Use specific Python versions for different scripts
- Easily update Python versions without affecting the script functionality
