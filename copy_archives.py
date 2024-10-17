import os
import subprocess
import re
from datetime import datetime, timedelta

# Paths to logs
original_log_path = '/var/ossec/logs/archives/archives.log'
copy_log_path = '/var/ossec/logs/archives/copy_archives.log'

# Function to append new logs from the original to the copy
def append_new_logs():
    with open(original_log_path, 'r') as original_log:
        original_lines = original_log.readlines()

    # Load the current copy log to check what has already been copied
    if os.path.exists(copy_log_path):
        with open(copy_log_path, 'r') as copy_log:
            copied_lines = copy_log.readlines()
    else:
        copied_lines = []

    # Append only new lines that are not already in copy_archives.log
    new_lines = original_lines[len(copied_lines):]

    with open(copy_log_path, 'a') as copy_log:
        copy_log.writelines(new_lines)

# Function to process the copied log and find entries for today
def process_logs_and_send():
    today = datetime.now().date()
    date_pattern = r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})'  # Regex pattern to match the date format
    today_logs = []

    with open(copy_log_path, 'r') as copy_log:
        for line in copy_log:
            match = re.search(date_pattern, line)
            if match:
                log_date = datetime.strptime(match.group(1), '%b %d %H:%M:%S')
                if log_date.date() == today:
                    today_logs.append(line)

    # If there are log entries for today, send them to S3
    if today_logs:
        date_str = today.strftime('%m-%d')
        new_log_name = f'security-logs-archives-{date_str}.log'

        # Create a new log file for today
        with open(new_log_name, 'w') as new_log:
            new_log.writelines(today_logs)

        # Send the new log to S3 using linode-cli
        command = f'/usr/local/bin/linode-cli obj put {new_log_name} security-logs/{date_str}'
        subprocess.run(command, shell=True)

        # Clear the copy log after sending
        open(copy_log_path, 'w').close()

# Main function
def main():
    append_new_logs()  # Step to append only new logs
    process_logs_and_send()  # Check for today's logs and send them

if __name__ == "__main__":
    main()
