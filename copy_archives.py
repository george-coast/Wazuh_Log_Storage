import os
import subprocess
import re
from datetime import datetime

# Paths to logs
original_log_path = '/var/ossec/logs/archives/archives.log'
copy_log_path = '/var/ossec/logs/archives/copy_archives.log'

# Function to append new logs to the copy without duplicating older logs
def update_copy():
    with open(original_log_path, 'r') as original_log:
        original_lines = original_log.readlines()

    if os.path.exists(copy_log_path):
        with open(copy_log_path, 'r') as copy_log:
            copy_lines = copy_log.readlines()
    else:
        copy_lines = []

    # Append only the new lines
    new_lines = original_lines[len(copy_lines):]
    with open(copy_log_path, 'a') as copy_log:
        copy_log.writelines(new_lines)

# Function to process the copied log and find the first entry of the next day
def process_logs_and_send():
    next_day_found = False
    last_date = None
    date_pattern = r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})'  # Regex pattern to match the date format

    with open(copy_log_path, 'r') as copy_log:
        for line in copy_log:
            match = re.search(date_pattern, line)
            if match:
                log_date = datetime.strptime(match.group(1), '%b %d %H:%M:%S')
                if log_date.day != datetime.now().day:
                    next_day_found = True
                    last_date = log_date
                    break

    if next_day_found:
        # Create a new log file for the current day and send it to S3
        date_str = (last_date - timedelta(days=1)).strftime('%m-%d')  # Previous day's date
        new_log_name = f'security-logs-archives-{date_str}.log'

        with open(new_log_name, 'w') as new_log:
            with open(copy_log_path, 'r') as copy_log:
                new_log.write(copy_log.read())

        # Send the new log to S3 using linode-cli
        command = f'/usr/local/bin/linode-cli obj put {new_log_name} security-logs/{date_str}'
        subprocess.run(command, shell=True)

        # Clear the copied log file after sending
        open(copy_log_path, 'w').close()

# Main function
def main():
    update_copy()
    process_logs_and_send()

if __name__ == "__main__":
    main()
