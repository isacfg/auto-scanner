# Export contract

This contract defines a lossless, unambiguous Finder export from the Auto Scanner Library. Export copies immutable Asset payloads; it never changes the Library, marks an Asset current, or creates a new image derivative.

## Export selection

An Export is a snapshot of an explicit ordered selection of Photographs. Before writing begins, the app resolves and freezes the UUID, digest, and source payload of every selected Asset so later Library edits cannot mix versions within the package.

For each Photograph, the user chooses:

- **Front only** or **Front and Back**;
- the current Front Master, or exactly one explicitly selected completed Front Restoration, as the Front Export Rendition.

The default Front Export Rendition is the current Front Master. The app must never infer a Restoration from creation time, completion time, list order, or a label such as “latest” or “best”. A Restoration is eligible only when it has a durable image payload and derives from the Photograph's current Front Master at the moment selection is frozen. Historical Restorations remain visible in history but are not eligible for a new export unless their Master becomes current again.

When Back is requested, its Export Rendition is its current Master. Back Restoration is outside the product contract. A Photograph without a durable current Back Master cannot be exported as Front and Back; the app must identify it before writing and allow the user to exclude it or switch it to Front only. Original Assets and superseded Masters are not Finder export renditions in the MVP.

The role recorded for each Side is its role when selection is frozen. Swapping Front and Back after that point does not alter an export already in progress.

## Package layout

One Export produces one self-contained directory:

```text
Auto Scanner Export 2026-07-18 143052/
├── manifest.json
├── 0001-photo-a1b2c3d4/
│   ├── front-master.heic
│   └── back-master.heic
└── 0002-photo-e5f6a7b8/
    └── front-restoration-91ab2c3d.png
```

The timestamp uses the user's local Gregorian calendar and 24-hour time at the start of export, with format `yyyy-MM-dd HHmmss`. It is a human aid, not identity. The Manifest's `exportId`, a client-generated UUID, is the Export Package identity.

Photograph directories use the frozen export order, zero-padded to at least four digits, followed by `photo-` and the first eight lowercase hexadecimal characters of the Photograph UUID without separators. The order prefix makes Finder sorting deterministic; the short UUID makes names stable and distinguishable. The full UUID in the Manifest is authoritative. A package cannot contain the same Photograph twice.

Image names are semantic within their Photograph directory:

- `front-master.heic`
- `front-restoration-<asset-short-id>.png`
- `back-master.heic`

`<asset-short-id>` is the first eight lowercase hexadecimal characters of the Asset UUID without separators. The selected Front mode makes `front-master.heic` and `front-restoration-….png` mutually exclusive. Back is absent from a Front-only export. File and directory names use ASCII except for the fixed package prefix, contain no user metadata, and do not depend on captions or dates that may later change.

## Formats and bytes

Every image is copied byte-for-byte from its immutable Library Asset:

- Master: HEIF payload with `.heic` extension;
- Restoration: lossless PNG payload with `.png` extension.

Export performs no resizing, recompression, color conversion, metadata rewrite, orientation change, or DPI injection. Pixel dimensions, color space, encoded metadata, and SHA-256 digest therefore remain those of the selected Asset. Conversion to JPEG or other share-oriented formats is not part of the MVP export contract.

## Manifest

The root `manifest.json` is UTF-8 JSON, encoded with deterministic key ordering for testability. It uses this top-level shape:

```json
{
  "schemaVersion": 1,
  "exportId": "6d5f20a4-6f61-48bc-8a97-f1bfd29dc69f",
  "createdAt": "2026-07-18T17:30:52Z",
  "application": {
    "name": "Auto Scanner",
    "version": "1.0",
    "build": "1"
  },
  "photographs": []
}
```

Each entry in `photographs`, in export order, contains:

- `photographId` and `order`;
- `directory`, relative to the package root;
- `sides`, containing one Front entry and, when requested, one Back entry.

Each side entry contains:

- `sideId` and `roleAtExport` (`front` or `back`);
- `rendition` (`master` or `restoration`);
- `assetId`, `assetKind`, `mediaType`, `relativePath`, `byteCount`, `pixelWidth`, `pixelHeight`, `sha256`, and `createdAt`;
- `originalAssetId` and `masterAssetId`, preserving the selected Asset's lineage; for a Master, `assetId` equals `masterAssetId`;
- for a Restoration, `restoration` with provider, model, immutable model version, request parameters, and completion timestamp.

Paths in the Manifest use `/` separators, are relative, normalized, and must not contain `..`, an absolute root, or a symbolic link. UUIDs use canonical lowercase hyphenated representation. Timestamps use UTC RFC 3339. Digests use 64 lowercase hexadecimal SHA-256 characters. The Manifest contains no provider token, remote request identity, cost, device metadata, capture-session identity, or sensitive location metadata; those are unnecessary to identify and verify exported renditions.

`schemaVersion` governs the entire document. Readers must reject an unsupported major value rather than guess. Additive fields may be introduced without changing version 1 only when existing fields keep their meaning and requiredness. Removing a field or changing its meaning requires a new schema version.

The package is valid only when every Manifest entry resolves to exactly one regular image file within the package, every image file other than `manifest.json` is referenced exactly once, and its byte count and SHA-256 digest match. The Manifest is the authority for identity and lineage; names are for Finder readability.

## Collision and atomicity rules

Export never overwrites or merges with an existing item. If the proposed package name exists, the app selects the first free Finder-style suffix — `Auto Scanner Export 2026-07-18 143052 2`, then `… 3`, and so on — while preserving the same `exportId` and contents.

The app writes to a uniquely named hidden sibling directory in the selected destination. It copies every image, verifies byte count and SHA-256 against the frozen selection, writes and verifies the Manifest last, synchronizes outstanding writes, and only then renames the staging directory to the reserved final name on the same volume. Reservation and final rename must fail if another item has acquired that name; the app then reserves a new suffix and retries only the rename.

Until the final rename succeeds, no final Export Package is visible. Cancellation, copy failure, verification failure, loss of destination access, or process termination leaves the Library untouched and no partial package at the final path. A later cleanup may remove an abandoned hidden staging directory identified by its `exportId`; it must never adopt it as a successful export or delete an unrelated directory. After the atomic rename succeeds, the Export is complete and is not rolled back if revealing it in Finder fails.

## Acceptance scenarios

1. Exporting a Front Master and Back Master yields two byte-identical HEIC files in one Photograph directory and two matching Manifest side entries.
2. Exporting a selected Restoration yields its byte-identical PNG, records its Original → Master → Restoration lineage, and does not also emit the Front Master.
3. Two Restorations completed at different times require an explicit choice; neither time nor list order selects one automatically.
4. A requested Back without a durable current Master is reported before any final package appears.
5. An existing package with the same timestamp is preserved and the new package receives the first free numeric suffix.
6. Failure after copying one image exposes no final package; retry creates a fresh staging directory and a single complete package.
7. Swapping Side roles after selection is frozen does not change the files or `roleAtExport` values in the running Export.
8. Recomputing every exported file's SHA-256 reproduces the digest recorded in the Manifest.
