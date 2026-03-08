#!/bin/bash
# Helper script for netpulse user to update systemd timer
# This script runs with sudo to update the timer configuration

set -e

# Check if interval is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <interval_minutes>"
    exit 1
fi

INTERVAL_MINUTES=$1

# Validate interval
if ! [[ "$INTERVAL_MINUTES" =~ ^[0-9]+$ ]] || [ "$INTERVAL_MINUTES" -lt 1 ] || [ "$INTERVAL_MINUTES" -gt 1440 ]; then
    echo "Error: Interval must be an integer between 1 and 1440"
    exit 1
fi

# Calculate systemd calendar format
if [ "$INTERVAL_MINUTES" -lt 60 ]; then
    # For intervals less than 60 minutes: *:0/{interval}:00
    CALENDAR_SPEC="*:0/${INTERVAL_MINUTES}:00"
elif [ "$INTERVAL_MINUTES" -eq 60 ]; then
    # Exactly one hour: hourly
    CALENDAR_SPEC="hourly"
elif [ "$INTERVAL_MINUTES" -lt 1440 ]; then
    # For intervals between 1-24 hours: *-*-* */{hours}:00:00
    HOURS=$((INTERVAL_MINUTES / 60))
    CALENDAR_SPEC="*-*-* */${HOURS}:00:00"
else
    # Daily
    CALENDAR_SPEC="daily"
fi

# Update timer file
TIMER_FILE="/lib/systemd/system/netpulse.timer"
TEMP_FILE="/tmp/netpulse.timer.tmp"

# Read current timer and update OnCalendar line
while IFS= read -r line; do
    if [[ "$line" =~ ^OnCalendar= ]]; then
        echo "OnCalendar=${CALENDAR_SPEC}"
    else
        echo "$line"
    fi
done < "$TIMER_FILE" > "$TEMP_FILE"

# Replace the timer file
mv "$TEMP_FILE" "$TIMER_FILE"

# Reload systemd and restart timer
systemctl daemon-reload
systemctl restart netpulse.timer

echo "SystemD timer updated to run every ${INTERVAL_MINUTES} minutes"
echo "Calendar specification: ${CALENDAR_SPEC}"
