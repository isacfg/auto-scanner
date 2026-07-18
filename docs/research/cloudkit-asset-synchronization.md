# Synchronize immutable photograph assets with CloudKit

## Decision

Use `CKSyncEngine` as the synchronization coordinator over one private CloudKit custom record zone. Keep a durable, authoritative local store on each device; CloudKit is the transport and cross-device replica, not the only copy or the UI's source of truth. Store immutable image payloads as `CKAsset` fields on separate Asset records, keep relationships and current pointers in metadata records, and preserve the UUIDs, lineage, SHA-256 digests, and tombstones defined by [ADR 0001](../adr/0001-photograph-asset-contract.md).

This is ready for implementation on iOS 26 and macOS 26. It avoids a bespoke synchronization protocol while retaining enough app-owned state to resume safely, expose progress, verify downloaded bytes, and resolve concurrent edits without overwriting image history.

## CloudKit model

Use the private database because the MVP is one person's library in one iCloud account. Put all library records in one custom zone so the client can consume zone changes incrementally and persist the `CKSyncEngine` state serialization between launches.

| Record type | Purpose | Important fields |
| --- | --- | --- |
| `LibraryPhotograph` | Photograph metadata and logical deletion | UUID, creation/session/order metadata, tombstone fields, domain revision |
| `LibrarySide` | Stable Side identity and mutable role/current selections | UUID, Photograph reference, role, current Original/Master UUIDs, tombstone fields, domain revision |
| `LibraryAsset` | One immutable Asset and, when present, its payload | UUID, Side/parent UUIDs, kind, media type, byte count, pixel dimensions, SHA-256, provenance, `CKAsset` payload, tombstone fields |

CloudKit record names are the client-generated domain UUIDs. References aid queries and inspection, but UUID fields remain the portable relationship contract in the local store. Image bytes never share a mutable record with Side roles or current pointers. An Asset record is created once; its payload, ancestry, digest, and dimensions are immutable thereafter.

Mutations that are atomic in the domain, such as installing a new Original/Master pair or swapping Side roles, are represented locally as one committed domain transaction with a monotonically increasing domain revision. The client then submits all affected records in one CloudKit record-zone save operation. Other devices apply a received batch to their local store transactionally and expose the new revision only when every referenced record and required payload is locally valid.

## Offline capture, upload, and resumption

Capture completes against local durable storage without waiting for iCloud. Before the UI calls a Photograph locally durable, write the Original and Master to app-managed files, calculate and persist their SHA-256 digests and metadata, and commit the local metadata transaction. The outbox then makes those records eligible for `CKSyncEngine` upload.

`CKAsset` is file-backed: keep the source file at a stable app-owned URL until CloudKit reports the corresponding pending record save as successfully sent. Do not use a temporary capture URL whose lifetime ends with an operation. A failed or interrupted transfer remains pending and is retried through the engine after relaunch or connectivity recovery; persist the engine state whenever it changes. CloudKit may schedule work opportunistically, so the app must also request fetch/send work at foreground and other product-appropriate opportunities instead of promising immediate background completion.

There is no product requirement for byte-range continuation of a partially transferred asset. The supported resumption contract is idempotent whole-record retry: immutable UUIDs and payload digests make repeat attempts safe. The app must not mark an Asset synchronized merely because its metadata record exists remotely; the record save and verified payload availability are one synchronization outcome.

## Local cache and integrity

The local store owns metadata and synchronization bookkeeping. Image payload storage has two classes:

- durable local originals and current masters created or explicitly retained on this device;
- evictable downloaded or superseded payload cache that can be reacquired from CloudKit.

Never evict a locally created payload while its Asset save is pending or failed, or while a live current pointer would otherwise have no verified local or remote copy. After durable upload, cache eviction may use least-recently-used order, protecting payloads currently displayed, exported, edited, or restored. Keep all metadata, digests, tombstones, and lightweight thumbnails needed for the library UI even when a full-resolution payload is evicted. Storage thresholds should be implementation configuration derived from available disk space, not a domain constant in this decision.

On every locally produced or downloaded payload, verify byte count and SHA-256 before installing it at its final content-addressed cache URL. Write to a staging URL and rename atomically only after verification. A mismatch is `integrityFailed`: quarantine/delete the staging bytes, retain the expected metadata, and refetch. Repeated mismatch is visible and must never replace a known-good local copy.

## Visible synchronization state

Derive one per-Photograph state from its Photograph, live Sides, current Assets, tombstones, and outbox/inbox work:

- `localOnly`: locally durable, but no required record has reached CloudKit yet;
- `uploading`: at least one required record or payload is being sent;
- `synced`: all live metadata and required current payloads are durably saved remotely and no relevant local mutation is pending;
- `downloading`: remote metadata is applied but a requested/current payload is not yet verified locally;
- `pendingDeletion`: a local tombstone has not yet been acknowledged remotely;
- `offline`: work is pending and the engine cannot currently reach CloudKit; retain the underlying pending direction for recovery;
- `needsAttention`: account, quota, permission, integrity, or non-retryable synchronization failure requires user action.

Transient retryable CloudKit errors stay in the pending state and show concise last-error context, not a false terminal failure. Progress may be reported per asset when available but must not be treated as durable state. A Photograph is `synced` only when every record needed to reconstruct its visible current state is acknowledged.

## Conflicts and non-destructive merge

Immutable Asset records merge by UUID: identical UUID and digest is the same Asset; the same UUID with different immutable fields or digest is an integrity violation and becomes `needsAttention`, never last-writer-wins.

For mutable Photograph and Side metadata, save with CloudKit change tags and handle `serverRecordChanged`. Merge fields according to domain semantics, using the common ancestor supplied by CloudKit when available:

- tombstone wins over later ordinary edits to the same identity;
- append-only Assets and restoration attempts are unioned;
- edits to distinct fields are combined;
- a current-pointer or role change wins only when the other side did not change that same field from the ancestor;
- concurrent incompatible pointer changes or role swaps preserve every Asset lineage, choose the deterministic winner by `(domainRevision, modifiedAt, deviceID)`, and record the losing mutation as conflict history eligible for an explicit redo/reselection.

The deterministic tie-breaker is only for converging the selected pointer/role, never for deleting payloads. Apply merged records locally in a single transaction and enqueue the merged server-facing record, so all devices converge. Do not silently retry a rejected mutable record with `.changedKeys` or overwrite the server record without performing this merge.

## Tombstones and physical purge

Domain deletions are explicit tombstone fields on the same stable record identity (`deletedAt`, deletion revision, and deleting device). Do not rely on immediate CloudKit record deletion as the deletion signal: a device can be offline longer than CloudKit's change history is convenient to replay, and physical deletion would discard the domain evidence needed for deterministic cascade and conflict handling.

Retain tombstone records indefinitely for the MVP; their metadata cost is small and the personal library has no server compaction requirement yet. Once a tombstone is acknowledged remotely and applied locally, payload bytes may be removed from caches when no live record references them. Do not physically delete CloudKit records or assets in the MVP. A future compactor requires a separate decision with a multi-device acknowledgement/watermark protocol.

## Zones, account changes, and limits

Use one custom zone for the entire private library. This gives one ordered change stream and permits atomic saves for coupled metadata without creating cross-zone dependencies. Do not create a zone per Photograph or Capture Session. If scale measurements later show that one zone is operationally inadequate, repartitioning is a migration decision, not speculative MVP complexity.

Treat CloudKit limits and quotas as runtime constraints, not hard-coded product promises. Chunk save batches below the service's per-operation limits, honor `CKErrorRetryAfterKey`, cap concurrent asset transfers, and surface quota/account failures as `needsAttention`. Before enabling sync, check account availability; on account change or zone reset, preserve unsent local captures, reset the CloudKit replica/engine state, recreate the zone if appropriate, and reconcile from the durable local store instead of deleting local originals.

## Acceptance criteria for implementation

- Capture and completion work with no network and survive process termination.
- Relaunch resumes pending record/asset work without duplicate domain identities.
- A Mac can reconstruct a Photograph only from verified records/assets and sees a meaningful state while payloads download.
- Concurrent recapture, crop edit, Side swap, restoration creation, and deletion never overwrite immutable bytes or lose a lineage.
- Corrupted or truncated payloads fail SHA-256 verification and never replace a valid cached asset.
- Deletion converges after either device has been offline, without resurrecting the Photograph.
- Cache eviction never removes the last unsynchronized copy and an evicted synchronized payload can be fetched again.
- Account, quota, retryable network, and integrity failures map to the visible state contract above.

## Official references

- Apple, [Synchronizing a local store to the cloud](https://developer.apple.com/documentation/CloudKit/synchronizing-a-local-store-to-the-cloud) — `CKSyncEngine` architecture, persisted state, pending changes, event handling, and local-store reconciliation.
- Apple, [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine) — synchronization engine for private-database record zones.
- Apple, [CKAsset](https://developer.apple.com/documentation/cloudkit/ckasset) — file-backed large payload field and file-lifetime requirements.
- Apple, [CKRecordZone](https://developer.apple.com/documentation/cloudkit/ckrecordzone) — custom zones and zone-scoped record organization.
- Apple, [CKModifyRecordsOperation](https://developer.apple.com/documentation/cloudkit/ckmodifyrecordsoperation) — batched record saves and atomic save policy within a zone.
- Apple, [CKError](https://developer.apple.com/documentation/cloudkit/ckerror) — retry, quota, account, partial failure, and server-record conflict handling.
- Apple, [Designing for CloudKit](https://developer.apple.com/icloud/cloudkit/designing/) — container environments, private database behavior, quotas, and schema considerations.
