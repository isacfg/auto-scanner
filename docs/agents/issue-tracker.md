# Local Markdown Issue Tracker

This repository uses Markdown files under `docs/wayfinder/` for Wayfinder maps and tickets.

## Wayfinding operations

### Storage

Each effort has one directory:

```text
docs/wayfinder/<effort>/
├── map.md
└── tickets/
    └── <stable-id>-<short-name>.md
```

Maps and tickets use YAML frontmatter. A map has `kind: map` and `labels: [wayfinder:map]`. A ticket has `kind: ticket`, a single `wayfinder:<type>` label, a `parent` path, and a stable `id`.

### Claiming

An open ticket is unclaimed when `assignee: null`. Claim it before work by setting `assignee` to the developer's GitHub login or stable agent name. Never claim more than one ticket in a Wayfinder session.

### Dependencies and frontier

Because Markdown has no native dependency relationship, tickets use `blocked_by`, an array of stable ticket ids. A ticket is unblocked when every referenced ticket has `status: closed`.

The frontier consists of tickets that are:

- children of the map;
- `status: open`;
- `assignee: null`;
- unblocked.

List ticket metadata with:

```sh
rg -n '^(id|title|status|assignee|blocked_by):' docs/wayfinder/<effort>/tickets
```

Resolve ids by searching the exact id:

```sh
rg -l '^id: <ticket-id>$' docs/wayfinder/<effort>/tickets
```

### Resolution

Record the answer under `## Resolution`, set `status: closed`, and append one linked one-line gist to the parent map's `## Decisions so far`. Do not duplicate the detailed resolution in the map.

When a resolution exposes a new precise question, add a ticket first and then wire its `blocked_by` ids. When fog becomes precise, remove it from `## Not yet specified` and represent it only in its new ticket.

