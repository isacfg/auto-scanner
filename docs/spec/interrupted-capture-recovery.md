# Interrupted capture recovery

This specification defines how the iPhone MVP preserves or discards an In-progress Photograph when the process ends before capture completes. It extends the capture state machine and asset contract without restoring stale camera observations or exposing incomplete work to the shared Library.

## Invariants

- A Capture Session has at most one In-progress Photograph. Its Photograph UUID, session order, frozen Back Capture requirement, and logical checkpoint are durable before the Front photo request begins.
- A Side is confirmed only when its Original, Master, metadata, warnings, and current pointers have been promoted as one logical transaction. A camera callback, encoded file, thumbnail, or partially written database row is not a confirmed Side.
- An In-progress Photograph is local-only. It is not counted as completed, shown on the Mac, exported, restored, or enqueued for CloudKit until completion is committed.
- Relaunch restores durable domain facts, never preview frames, gate readiness, timers, detected quadrilaterals, removal latches, or an in-flight camera request.
- Recovery is idempotent. Repeating it cannot create another Photograph, Side, Asset lineage, counter increment, or upload.
- Asset UUIDs are never reused. Bytes found without a committed Asset record are never adopted by filename or content similarity.

## Durable checkpoints

The app persists one checkpoint for the In-progress Photograph:

- `frontPending`: the identity and frozen Back Capture requirement exist, but no Front is confirmed;
- `frontConfirmedAwaitingRemoval`: the Front is durable and the app had not yet observed its stable removal;
- `frontConfirmedAwaitingBack`: the Front is durable, removal had been observed, and Back is still required;
- `backConfirming`: Back promotion may have been interrupted;
- `completing`: all required Sides are durable and completion promotion may have been interrupted.

Transient `evaluating` and `capturing` substates collapse to the matching pending checkpoint after termination. Pause state and timeout progress are not restored. When Back Capture was off, successful Front promotion and Photograph completion occur in the same recovery-capable completion sequence; the app does not leave a user-visible Front-only draft between them.

## Atomic side promotion

Every capture attempt has a distinct attempt UUID and writes only inside an app-owned staging directory. Original and Master bytes are fully encoded, synchronized, measured, and hashed there before metadata can reference them.

Promotion uses a durable journal and this order:

1. record the intended Photograph, Side, attempt, Asset UUIDs, final paths, sizes, and digests;
2. atomically rename both immutable payloads to their final app-owned paths on the same volume and synchronize the containing directory;
3. in one local-store transaction, insert both Asset records, link Master to Original, set the Side's current pointers and capture metadata, advance the Photograph checkpoint, and mark the journal committed;
4. only after that transaction succeeds, emit confirmation feedback or advance the completed counter.

The metadata commit is the domain commit point. A crash before it leaves no confirmed Side. A crash after it leaves a fully reconstructible Side. Recovery first replays the journal: a committed transaction is accepted after verifying both referenced payloads; an uncommitted intent is rolled back and its files are removed. It never completes a transaction by guessing from the presence of files. A committed record with a missing or mismatched payload is an integrity failure that blocks capture recovery and requires attention; it is not silently downgraded or recaptured.

## Relaunch behavior

Before starting the camera or synchronization, launch recovery replays the promotion journal and completion transaction, verifies the current payloads of the In-progress Photograph, and reconstructs its checkpoint.

- `frontPending` resumes at `awaitingFrontPlacement`. The existing Photograph identity and frozen Back Capture requirement remain; the next accepted Front attempt creates its first lineage.
- `frontConfirmedAwaitingRemoval` resumes with the saved Front thumbnail and requires a newly observed stable absence before Back placement can be accepted. Camera presence at launch never satisfies the old removal latch.
- `frontConfirmedAwaitingBack` resumes at `awaitingBackPlacement`, but clears all readiness and requires a newly detected, stable candidate. If a photograph is already present, the UI asks the user to lift and replace it before capture, so a stale Front cannot be classified as Back.
- `backConfirming` first replays promotion. A committed Back advances to completion; an uncommitted Back attempt is removed and resumes at `frontConfirmedAwaitingBack` without changing the Front.
- `completing` replays completion. The Photograph becomes visible, countable, and sync-eligible exactly once, then resumes at `awaitingCompletedRemoval` if a candidate is present or `awaitingFrontPlacement` after a newly observed stable absence.

Camera permission loss or camera unavailability leaves the recovery choice visible but disabled for continuation until the camera is usable. No checkpoint automatically fires a capture on launch.

## Recovery experience and commands

An unresolved In-progress Photograph gates starting another Capture Session. Relaunch presents a recovery sheet before the live scanner, using the durable Front thumbnail when one exists and stating whether the app is waiting for Front or Back.

- **Continue capture** resumes the checkpoint under the revalidation rules above.
- **Skip Back** is available only with a confirmed Front and frozen Back Capture on. It completes that same Photograph exactly as in the normal state machine.
- **Discard Photograph** requires confirmation when a Front is durable. It atomically marks the draft discarded, removes it from the session's pending order, and then cleans its local-only metadata and payloads. It does not create a completed Photograph or CloudKit tombstone because the draft was never published.
- With no confirmed Side, discard is immediate because only the reserved identity and staging work exist.

The user cannot defer a draft and begin another capture in the MVP. This keeps the single-current-cycle invariant and avoids an unrequested draft browser. Completed Photographs continue to use normal undo, redo, deletion, and tombstone behavior; this discard command applies only to an unpublished In-progress Photograph.

## Orphan cleanup

Cleanup runs after journal replay at launch and may run periodically while no promotion is active. It is restricted to app-owned capture staging and final-asset directories.

- abandoned staging directories whose attempt UUID is not active in the journal are deleted;
- payloads at final paths with no committed Asset record are deleted only after all journal entries have been resolved;
- committed payloads, payloads referenced by a live or discarded transaction awaiting cleanup, and unsynchronized completed Assets are never treated as orphans;
- unexpected files outside the app-owned layout are ignored and reported rather than deleted.

Cleanup is retryable. Failure to remove an orphan does not corrupt or complete a Photograph; it records diagnostics and retries later. The app never imports an orphan into the Library.

## Acceptance scenarios

1. Terminating after reserving the Photograph but before the Front callback relaunches with the same identity at Front placement and creates no Asset.
2. Terminating after only one staged payload exists removes the attempt and resumes Front capture without a half Side.
3. Terminating after both final payload renames but before metadata commit rolls back the journal and deletes unreferenced bytes.
4. Terminating after the Front commit with Back required shows the Front thumbnail and offers Continue, Skip Back, or confirmed Discard; it never syncs the draft.
5. Relaunch with the Front still under the camera cannot capture it as Back until a new stable absence and placement are observed.
6. Terminating during Back promotion either recovers the committed Back or discards only that attempt and preserves the Front.
7. Terminating during completion increments the session counter and enqueues synchronization exactly once.
8. Repeating launch recovery or orphan cleanup produces the same domain state and never adopts unrelated bytes.
9. Discarding a local-only draft leaves no Photograph in the completed Library and permits the next capture to use a new UUID and the next available session order.
