import os
import re
import signal
import subprocess  # This is necessary for pgrep command
from datetime import datetime

# Paths to the logs
alerts_log_path = '/var/ossec/logs/alerts/copy_alerts.log'
archives_log_path = '/var/ossec/logs/archives/copy_archives.log'

# Function to check if the next day's log exists
def check_next_day_logs(log_path):
    date_pattern = r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})'  # Regex pattern to match the date format
    next_day_found = False

    with open(log_path, 'r') as log_file:
        for line in log_file:
            match = re.search(date_pattern, line)
            if match:
                log_date = datetime.strptime(match.group(1), '%b %d %H:%M:%S')
                if log_date.day != datetime.now().day:  # Check if the log entry is for the next day
                    next_day_found = True
                    break

    return next_day_found

# Function to terminate both scripts
def terminate_scripts():
    # Get the process IDs of the running scripts
    try:
        # Adjust the pgrep command to match the executable names
        alerts_pid = int(subprocess.check_output(["pgrep", "-f", "alerts_script.py"]).strip())
        archives_pid = int(subprocess.check_output(["pgrep", "-f", "archives_script.py"]).strip())
        
        # Terminate both scripts
        os.kill(alerts_pid, signal.SIGTERM)
        os.kill(archives_pid, signal.SIGTERM)
        print("Both scripts terminated.")
    except Exception as e:
        print(f"Error terminating scripts: {e}")

# Main function
def main():
    alerts_next_day = check_next_day_logs(alerts_log_path)
    archives_next_day = check_next_day_logs(archives_log_path)

    # If next day's logs are found, terminate the running scripts
    if alerts_next_day or archives_next_day:
        terminate_scripts()

if __name__ == "__main__":
    main()
