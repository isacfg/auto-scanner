# Use immutable, revisioned asset lineages for each photograph side

The library will model a physical Photograph separately from its stably identified Sides and immutable image Assets. Client-generated UUIDs make every record independently synchronizable; current pointers select the active Original and Master while explicit derivation links preserve provenance. This costs more metadata and storage than mutable files, but prevents destructive synchronization conflicts and makes redo, side swapping, restoration history, and eventual cleanup deterministic.

## Contract

### Identity and relationships

- `Photograph`, `Side`, and every `Asset` have independent, client-generated UUIDs that never change or get reused.
- A Photograph owns exactly one Side whose role is `front` and zero or one whose role is `back`. A Side belongs to exactly one Photograph.
- Front and Back are mutable roles of stable Side records, not identities. Swapping two captured sides atomically exchanges their roles; it does not copy bytes, change IDs, or rewrite derivation links.
- Each Side selects at most one current Original and one current Master. A Master references exactly one Original. A Restoration references exactly one Master and is valid only for a Side currently playing the Front role.
- Asset ancestry is append-only. No operation changes an Asset's owner or parent after creation.

### Image payloads and resolution

- An Original is the full-resolution HEIF camera payload (`public.heic`) emitted for the accepted capture. Its encoded bytes, pixel dimensions, color profile, and capture metadata are preserved; orientation is metadata and no crop, rotation, perspective correction, enhancement, or resampling is applied.
- A Master is an HEIF image (`public.heic`) in sRGB with orientation baked into its pixels. It is rendered from the selected Original at the largest pixel dimensions supported by the accepted crop and perspective transform, with no upscaling, and uses high-quality encoding suitable for repeated viewing and export.
- A Restoration is a lossless PNG (`public.png`) in sRGB with orientation baked in. It keeps the provider result's pixel dimensions, including a deliberate provider upscale, but is never silently resized after receipt.
- Pixel dimensions, not DPI, define resolution inside the Library. Export may add a DPI hint without changing the stored Asset.
- Every payload has a SHA-256 content digest. The digest verifies integrity and may detect duplicate bytes, but it is never the record's identity.

### Metadata

Every Asset records its UUID, kind, media type, byte count, pixel width and height, SHA-256 digest, creation timestamp, and derivation parent where applicable. An Original additionally records capture timestamp, EXIF orientation, color profile, camera/device metadata made available by the capture pipeline, and the Capture Session identity. A Master additionally records the accepted crop quadrilateral, rotation, perspective transform, and correction timestamp. A Restoration additionally records provider, model and model version, request parameters, status, request/completion timestamps, cost and currency, and provider request identity.

Photograph-level metadata records its UUID, creation timestamp, originating Capture Session, deletion state, and the stable order used by that session. Side-level metadata records its UUID, Photograph UUID, current role, capture timestamp, and pointers to its current Original and Master. User-facing captions, dates, and tags may be added later without changing this asset contract.

Sensitive location metadata is not retained. Device and camera metadata is descriptive provenance only and must not be used as identity.

### Lifecycle

- A Photograph becomes complete when its Front has a durable current Original and Master and either Back Capture is not required, the Back also has both, or the user explicitly skips the Back.
- Recapturing one Side creates a new Original and Master lineage, then atomically moves that Side's current pointers after both payloads are durable. The other Side is untouched. The replaced lineage becomes superseded; Restorations derived from it remain historical and never become current derivatives of the replacement Master.
- Re-editing geometry creates a new Master from the same current Original and moves only the current Master pointer. Existing Restorations remain attached to the superseded Master and visible as history.
- Creating or retrying restoration always creates a new Restoration record. Failed and cancelled attempts retain their metadata and have no image payload; a retry never mutates or replaces a prior attempt.
- Removing a Back tombstones that Side and its current pointers without affecting the Front. Adding a Back later creates a new Side identity. Skipping Back capture creates no placeholder Side or image Asset.
- Swapping sides is allowed only when both Sides exist. Their roles change atomically; after the swap, existing Restorations remain linked to their original Side and Master but are historical because only derivatives explicitly created from the current Front Master are current Front restorations.
- Deleting a Photograph is a logical tombstone that hides the Photograph and cascades to all owned Sides and Assets. Deleting one Side or one Restoration likewise creates a tombstone scoped to that record and its owned descendants; deleting an Original or Master directly is not a user operation while it is part of a live lineage.
- Superseded or deleted payloads are eligible for physical purge only after replacement or deletion is durably synchronized and no live record references them. Tombstone retention duration and local cache eviction are synchronization/storage policy, not part of this domain contract.

## Consequences

The apps can synchronize metadata and payloads independently without last-writer-wins mutation of image bytes. UI labels such as “redo” and “swap” operate on pointers or roles, while provenance remains intact. HEIF keeps camera and corrected assets compact; PNG avoids an extra lossy generation for AI output. Implementations must treat role exchange, current-pointer changes, and tombstoning as atomic domain mutations even if CloudKit persists their records in stages.
