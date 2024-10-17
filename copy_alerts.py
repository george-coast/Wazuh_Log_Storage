import os
import subprocess
import re
from datetime import datetime, timedelta

# Paths to logs
original_log_path = '/var/ossec/logs/alerts/alerts.log'
copy_log_path = '/var/ossec/logs/alerts/copy_alerts.log'

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

    # Append only new lines that are not already in copy_alerts.log
    new_lines = original_lines[len(copied_lines):]

    with open(copy_log_path, 'a') as copy_log:
        copy_log.writelines(new_lines)

# Function to process the copied log and find the last date
def process_logs_and_send():
    last_date = None
    date_pattern = r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})'  # Regex pattern to match the date format
    next_day_found = False

    with open(copy_log_path, 'r') as copy_log:
        for line in copy_log:
            if 'Oct' in line:  # Change this to match your log's date format
                match = re.search(date_pattern, line)
                if match:
                    last_date = match.group(1)
                    log_date = datetime.strptime(last_date, '%b %d %H:%M:%S')

                    # Check if the log entry is for the next day
                    if log_date.date() == (datetime.now().date() + timedelta(days=1)):
                        next_day_found = True
                        break

    # If next day's log is found, send the file to S3
    if next_day_found and last_date:
        date_str = log_date.strftime('%m-%d')
        new_log_name = f'security-alerts-{date_str}.log'

        # Create a new log file for the day
        with open(new_log_name, 'w') as new_log:
            with open(copy_log_path, 'r') as copy_log:
                new_log.write(copy_log.read())

        # Send the new log to S3 using linode-cli
        command = f'/usr/local/bin/linode-cli obj put {new_log_name} security-logs/{date_str}'
        subprocess.run(command, shell=True)

        # Clear the copy log after sending
        open(copy_log_path, 'w').close()

# Main function
def main():
    append_new_logs()  # Step to append only new logs
    process_logs_and_send()  # Check for next day and send logs

if __name__ == "__main__":
    main()
