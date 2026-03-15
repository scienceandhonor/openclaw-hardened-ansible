# remind-me

Set one-time or recurring reminders that are delivered through the OpenClaw agent.

## When to use

Use this skill whenever the user asks to be reminded of something at a future time or on
a recurring schedule. Examples:

- "Remind me in 30 minutes to take my medication"
- "Remind me tomorrow at 9am to call the dentist"
- "Remind me every weekday at 8am to check my email"
- "Set a reminder for next Friday at 5pm to send the weekly report"

## Implementation

### One-time reminders

Call `create-reminder.sh` with the message and time expression. The time expression
should be passed exactly as the user stated it — GNU `date -d` handles natural language
on Ubuntu/Debian.

```
bash ~/workspace/skills/remind-me/create-reminder.sh "<message>" "<time expression>"
```

Examples:
```
bash ~/workspace/skills/remind-me/create-reminder.sh "take medication" "in 30 minutes"
bash ~/workspace/skills/remind-me/create-reminder.sh "call the dentist" "tomorrow at 9am"
bash ~/workspace/skills/remind-me/create-reminder.sh "send weekly report" "next Friday at 5pm"
```

The script returns the scheduled time and job ID on success. Confirm to the user with
the exact scheduled time (e.g. "Reminder set for 14:35 today.").

### Recurring reminders

Call `create-recurring.sh` with the message and a cron expression (5-field standard
cron). Convert natural language to cron before calling.

```
bash ~/workspace/skills/remind-me/create-recurring.sh "<message>" "<cron expression>"
```

Examples:
```
bash ~/workspace/skills/remind-me/create-recurring.sh "check email" "0 8 * * 1-5"
bash ~/workspace/skills/remind-me/create-recurring.sh "drink water" "0 * * * *"
bash ~/workspace/skills/remind-me/create-recurring.sh "weekly report" "0 17 * * 5"
```

Confirm the schedule back to the user in plain language (e.g. "Set: every weekday at
8:00.").

## Managing reminders

To list all active reminders:
```
openclaw cron list
```

To remove a reminder by job ID (shown in `cron list` output):
```
openclaw cron rm <jobId>
```

## Log

Every scheduled reminder is appended to `$HOME/workspace/reminders.md`. You can show the
user the log with:
```
cat ~/workspace/reminders.md
```
