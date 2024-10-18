#!/bin/bash

# Start alerts script in the background
./alerts_script &
ALERTS_PID=$!

# Start archives script in the background
./archives_script &
ARCHIVES_PID=$!

# Run the termination script, passing the PIDs of the alerts and archives scripts
./termination_script $ALERTS_PID $ARCHIVES_PID

# After the termination script finishes, confirm the other scripts are terminated
wait $ALERTS_PID
wait $ARCHIVES_PID

echo "Alerts and Archives scripts have been terminated."
