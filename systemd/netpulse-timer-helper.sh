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
    # For intervals between 1-24 hours, use hourly with step
    HOURS=$((INTERVAL_MINUTES / 60))
    if [ "$HOURS" -eq 1 ]; then
        CALENDAR_SPEC="hourly"
    elif [ "$HOURS" -eq 2 ]; then
        CALENDAR_SPEC="*-*-* 00/2:00:00"
    elif [ "$HOURS" -eq 3 ]; then
        CALENDAR_SPEC="*-*-* 00/3:00:00"
    elif [ "$HOURS" -eq 4 ]; then
        CALENDAR_SPEC="*-*-* 00/4:00:00"
    elif [ "$HOURS" -eq 6 ]; then
        CALENDAR_SPEC="*-*-* 00/6:00:00"
    elif [ "$HOURS" -eq 8 ]; then
        CALENDAR_SPEC="*-*-* 00/8:00:00"
    elif [ "$HOURS" -eq 12 ]; then
        CALENDAR_SPEC="*-*-* 00/12:00:00"
    else
        CALENDAR_SPEC="*-*-* 00/${HOURS}:00:00"
    fi
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
