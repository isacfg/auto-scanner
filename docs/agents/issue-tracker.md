# GitHub Issue Tracker

This repository uses GitHub Issues as the canonical tracker.

## Wayfinding operations

The canonical Wayfinder map is the open issue labelled `wayfinder:map`. Its tickets are native GitHub sub-issues with exactly one of these labels:

- `wayfinder:research`
- `wayfinder:prototype`
- `wayfinder:grilling`
- `wayfinder:task`

### Load the map

```sh
gh issue list --label wayfinder:map --state open
gh issue view <map> --json number,title,body,state,subIssues,url
```

### Claim and frontier

An open sub-issue with no assignee is unclaimed. Native `blocked by` relationships define whether it is unblocked. Claim a ticket before reading beyond its question or doing work:

```sh
gh issue edit <ticket> --add-assignee @me
```

The frontier is the ordered set of open, unassigned sub-issues whose native blockers are all closed. Never resolve more than one ticket per Wayfinder session.

### Create and wire tickets

Create every ticket first, then add native dependency relationships in a second pass:

```sh
gh issue create --parent <map> --label wayfinder:<type> --title "<name>" --body $'## Question\n\n<question>'
gh issue edit <ticket> --add-blocked-by <blocking-ticket>
```

### Resolve

1. Commit and push any linked research or prototype asset.
2. Post the detailed answer as a resolution comment on the ticket.
3. Close the ticket.
4. Append one linked one-line gist to the map's `## Decisions so far`.
5. Create newly precise tickets and wire dependencies; remove graduated fog from the map.

Refer to every issue by its linked title in user-facing text, never by a bare number.

