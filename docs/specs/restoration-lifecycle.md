# Restoration lifecycle

This specification defines the macOS MVP contract for manually restoring one or more photographs with the pinned Replicate CodeFormer preset. It describes domain behavior and persistence, not UI layout or implementation structure.

## Invariants

- Only the current Master of a Side currently playing the Front role is eligible when selected. A Back, Original, existing Restoration, deleted record, or non-current Master is ineligible.
- Selection never starts remote work. Confirmation creates one immutable Restoration Attempt per still-eligible selected Front Master, all belonging to one Restoration Batch.
- Each Attempt binds the source Master identity and digest, provider, full model-version digest, parameters, estimated cost and currency at confirmation. Later edits, role swaps, or preset changes do not alter it.
- One Attempt can produce at most one Restoration. An Attempt and any resulting Restoration never overwrite the Master or another Restoration.
- Attempts proceed and terminate independently. A partial Batch is normal: completion, failure, cancellation, and uncertainty in one item do not roll back the others.
- Retry always creates a new Attempt and requires a fresh estimate and confirmation. No command rewinds or mutates a terminal Attempt.

## Manual batch selection and cost confirmation

The user enters selection mode explicitly and may add or remove eligible photographs individually, select all currently visible eligible photographs, or clear the selection. The app de-duplicates by current Front Master identity, preserves the library's visible order, and reports excluded items with a reason. Existing Restorations do not make a Master ineligible.

Before confirmation, the app calculates a Cost Estimate for every selected Master and the Batch total in USD using the current configured price rule for the pinned model version and the Master's stored dimensions. The estimate records the price rule/version, timestamp, per-item amount, total, and currency. It is non-binding because provider billing may depend on runtime and prices may change.

An estimate expires after 15 minutes or immediately if selection, source eligibility, model version, preset, price rule, or input dimensions change. An expired estimate must be recalculated. Confirmation must show provider, item count, per-item estimates, total estimate, currency, the preset, and the cloud-processing disclosure. The first confirmation also records consent to send Front Masters to Replicate; revoking that consent prevents new confirmations but does not erase history.

Immediately before creating the Batch, eligibility is checked again atomically. Ineligible items are removed and the changed total must be confirmed again. A confirmed Batch and all its queued Attempts are persisted before any upload begins.

## Queue and commands

The durable queue is FIFO by Batch confirmation time and then selection order. The MVP permits one Attempt in `submitting`, `processing`, `cancellationRequested`, or `downloading` at a time. This intentionally bounds network use and accidental spend; terminal or attention-required Attempts do not block later queued items.

Commands are:

- **Confirm Batch**: persist the Batch and its Attempts in `queued`.
- **Cancel Attempt**: cancel a `queued` Attempt locally, or request remote cancellation for an Attempt with a provider identity. Cancellation of a `submitting` Attempt without a provider identity is deferred until submission outcome is known.
- **Cancel remaining Batch**: apply Cancel Attempt to every non-terminal Attempt in that Batch; completed items remain completed.
- **Check status**: query the existing provider prediction; it never creates another prediction.
- **Retry Attempt**: preselect only the same source Master for a new estimate and confirmation. If that Master is no longer the current Front Master, the user must instead start from the current eligible Master.
- **Compare**: open the completed Restoration against the exact source Master to which it is linked.
- **Delete Restoration**: tombstone the successful Restoration under the asset contract. It does not remove the Attempt from history.

Repeated commands are idempotent with respect to an Attempt: they must not create a second provider prediction or a second Restoration. A command rejected for the current state leaves the Attempt unchanged.

## States and transitions

| State | Meaning | Allowed next states |
|---|---|---|
| `queued` | Durable and not submitted | `submitting`, `cancelled` |
| `submitting` | The create-prediction request is in flight; no durable provider identity is yet known | `processing`, `submissionUnknown`, `cancellationRequested` |
| `submissionUnknown` | The create request may have succeeded, but no provider identity was received | `processing`, `failed`, `cancelled` |
| `processing` | A provider identity is durable and the remote prediction is starting or running | `processing`, `cancellationRequested`, `downloading`, `failed`, `cancelled` |
| `cancellationRequested` | Remote cancellation was requested but is not yet terminal | `cancellationRequested`, `downloading`, `failed`, `cancelled` |
| `downloading` | Provider succeeded; output is being validated and made durable | `completed`, `failed` |
| `completed` | Output is durable as exactly one Restoration | none |
| `failed` | This Attempt cannot complete; the reason is durable | none |
| `cancelled` | This Attempt will do no further work | none |

`completed`, `failed`, and `cancelled` are terminal. Provider `starting` and `processing` both map to local `processing`; provider `succeeded` enters `downloading`; provider `failed` enters `failed`; and provider `canceled` enters `cancelled`.

Cancellation is best effort. For a queued Attempt it is immediate and has no provider cost. For submitted work the app calls the persisted cancel URL, continues polling, and does not claim that cost was avoided. If success wins the race with cancellation, the Attempt proceeds through `downloading` to `completed` so a paid result is not discarded. Cancel remaining Batch does not delete any record.

`submissionUnknown` exists for the irreducible crash or network-loss window after Replicate may have accepted a POST but before its prediction identity became durable. The app must never automatically issue a second POST from this state. While the provider still exposes recent API predictions, Check status may reconcile an unambiguous matching prediction by account, pinned version, creation window, and input; otherwise the Attempt stays uncertain. The user may explicitly abandon it as `cancelled`, or choose Retry through a new cost confirmation after being warned that the original may also incur cost. If Replicate confirms no prediction exists, it becomes `failed` with reason `submissionNotAccepted`.

## Polling, deadlines, and retry

Each submitted prediction uses Replicate's `Cancel-After` value of 15 minutes. While the Mac app is active, it polls the persisted get URL after 1 second, then 2, 4, 8, 15, and every 30 seconds, adding up to 20% jitter. A request has a 30-second transport timeout. Successful responses reset consecutive transport failures; server rate-limit guidance takes precedence when it asks for a longer delay.

A transport timeout, offline state, app suspension, or polling failure is not a provider failure and does not create a new Attempt. After five consecutive polling failures, automatic polling pauses for five minutes, the Attempt remains in its current state, and Check status remains available. On network recovery or app relaunch, polling resumes against the same provider identity. The 15-minute provider deadline bounds remote execution; only a provider terminal response determines `failed` or `cancelled`.

Retry is offered for `failed`, `cancelled`, and deliberately abandoned `submissionUnknown` Attempts, never for `queued`, `submitting`, `processing`, `cancellationRequested`, or `downloading`. It is also offered after output download/validation failure, but still creates a new provider prediction because Replicate output retention may have expired. The previous Attempt remains unchanged and the new Attempt stores `retryOfAttemptID` for history.

## Successful result persistence

On provider success the app downloads the output immediately, accepting only a decodable `public.png` whose dimensions and non-empty payload can be measured. It computes SHA-256, records byte count and actual dimensions, writes the payload to a temporary local file, and atomically promotes both payload and Asset metadata into the Library as a Restoration derived from the bound Master. Only then does the Attempt become `completed`.

If download, validation, or durable promotion fails, the Attempt becomes `failed` with a stable reason and no Restoration Asset. A partially written payload is not an Asset and may be cleaned up. The app never marks completion from provider status alone. Provider-reported cost is stored as actual cost when available; otherwise actual cost is explicitly unknown and the confirmed estimate remains visible, never relabelled as actual.

## Durable history and comparison

The local library persists every Batch and Attempt, including source Master ID and digest, Batch and retry links, provider prediction ID and URLs when known, pinned model version, parameters, state, timestamps for every transition, estimate, actual cost or unknown marker, cancellation timestamp, stable failure reason, and resulting Restoration ID. Secrets, bearer tokens, uploaded bytes, and transient signed input/output URLs are not synchronized as history; only the minimum provider identity needed for recovery is retained.

History is chronological and shows every Attempt, not just successful outputs. A Batch summary derives counts and estimated/actual totals from its Attempts. A superseded source Master or later Side-role swap makes an Attempt historical but does not rewrite or hide it. Comparison is available only for a non-tombstoned completed Restoration and always pairs it with its exact source Master, even when that Master is no longer current. If either payload is not local, it must be fetched from the Library's synchronized storage before comparison.

## Recovery after termination

On launch, the app first repairs any interrupted local atomic promotion, then reconstructs the FIFO queue from persisted Attempts:

1. `queued` Attempts remain queued.
2. `processing` and `cancellationRequested` Attempts with a provider identity run Check status before new queue work.
3. `downloading` Attempts query the provider and resume download if output is still available. If the output has expired and no durable local payload exists, they become `failed` with reason `outputExpiredBeforePersistence`.
4. `submitting` without a provider identity becomes `submissionUnknown`; it is never silently resubmitted.
5. `submissionUnknown` remains attention-required until reconciled or explicitly abandoned.
6. Terminal Attempts remain unchanged.

Recovery is deterministic and may be repeated. Queue progress resumes only after recovery checks for previously submitted work finish, preventing a relaunch from increasing concurrency or duplicating spend.

## Acceptance scenarios

- Selecting ten eligible photographs and confirming once durably creates one Batch and ten queued Attempts before the first network request; cancelling one does not affect the other nine.
- Editing a selected Master before confirmation removes it and requires confirmation of the new total; editing it after confirmation does not retarget its existing Attempt.
- Quitting during provider processing and reopening checks the same prediction ID and eventually stores exactly one Restoration.
- Losing the network during the submission response creates `submissionUnknown` and never causes automatic duplicate submission.
- Cancelling while remote work races to success keeps and persists the successful paid output.
- A provider success followed by an invalid or expired output never appears as completed.
- Retrying a failed Attempt creates a separately estimated and confirmed Attempt linked to the prior one; both remain visible in history.
- Re-editing or swapping the source Side after completion keeps historical comparison tied to the exact original source Master.
