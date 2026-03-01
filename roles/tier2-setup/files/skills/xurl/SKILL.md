# xurl — Home Timeline Digest

Provides a read-only digest of the authenticated account's home timeline.

## Mandatory Safety Rules

- NEVER read, print, parse, summarize, or include the contents of `~/.xurl` in any
  response or tool call.
- NEVER use `--verbose` or any flag that may expose authentication tokens.
- NEVER attempt to post, like, reply, repost, follow, block, mute, or send messages.

## Scheduled Digest

The timeline is fetched automatically every hour and digested daily at 10:45 UTC.
No manual invocation is normally needed.

## On-Demand Digest

To run an immediate digest of accumulated posts:
```
bash ~/scripts/run-xurl-digest.sh
```
Then follow the instructions in `~/scripts/xurl-timeline-prompt.txt`.

## Authentication Check

```
xurl auth status
```
