# Auto Scanner Domain Glossary

The Auto Scanner domain describes a private library of physical photographs and the digital assets derived from capturing them.

## Library

**Library**:
The user's collection of Photographs, their Sides, Assets, and processing state shared between the iPhone and Mac apps.

**Capture Session**:
A continuous period in which a user digitizes multiple Photographs on the iPhone.

**In-progress Photograph**:
A Photograph whose Front capture has begun but which has not yet been completed or discarded. Its Back Capture requirement is fixed when Front capture begins.

**Manual Exception Capture**:
An explicit capture made available after automatic capture has waited too long. It accepts quality warnings but still requires a detectable Photograph, an available camera, and no capture already in progress.

**Supported Capture**:
A Capture Session performed with the iPhone stationary in a stand above the Photograph.

**Handheld Capture**:
A Capture Session performed while the user holds the iPhone.

**Back Capture**:
An optional Capture Session mode in which both Sides of a Photograph are captured and linked; it is disabled by default.

## Photograph and sides

**Photograph**:
A single physical printed photograph represented in the Library. A Photograph always has one Front and may have one Back.

**Side**:
One physical face of a Photograph with a stable identity and exactly one current role, Front or Back.
_Avoid_: Page, image

**Front**:
The role of the primary image-bearing Side of a Photograph.

**Back**:
The role of the optional reverse Side of a Photograph; it is not eligible for AI restoration by default.

## Assets

**Asset**:
An immutable image payload with its own identity and metadata, belonging to one Side either directly or through another Asset.
_Avoid_: File, version

**Original**:
The immutable camera output for one Side of a Photograph and the root of that Side's derivation lineage.
_Avoid_: Raw

**Master**:
The accepted, non-AI geometric correction of one Original, with crop, rotation, and perspective correction applied.
_Avoid_: Edited original

**Restoration**:
An immutable AI-produced derivative of one Front Master. Multiple Restorations may coexist without replacing the Master or one another.
_Avoid_: Restored master

**Restoration Attempt**:
An immutable record of one confirmed request to produce a Restoration from one specific Front Master. It remains in history whether it completes, fails, is cancelled, or has an uncertain submission outcome; retrying creates another Attempt.
_Avoid_: Job, retry

**Restoration Batch**:
A user-confirmed group of Restoration Attempts created from one manual selection and one Cost Estimate. Attempts in the Batch proceed independently and may finish differently.
_Avoid_: Bulk restoration

**Cost Estimate**:
A time-bounded, non-binding projection of Restoration cost in a named currency, recorded per selected Front Master and as a Batch total before confirmation.
_Avoid_: Quote, final cost

**Current Asset**:
The active Original or Master selected for a Side; older lineages may remain as history but are not current.
_Avoid_: Latest asset

**Superseded Asset**:
An Asset retained as history after another Asset becomes current in the same role.
_Avoid_: Deleted asset

## Export

**Export Package**:
A self-contained Finder folder produced by one Export, containing selected renditions and a Manifest that preserves their Library identities and provenance.
_Avoid_: Export folder, archive

**Export Rendition**:
The specific Asset selected to represent a Side in an Export Package: the current Master or, for the Front, one explicitly selected completed Restoration.
_Avoid_: Latest version, best version

**Manifest**:
The versioned machine-readable inventory that maps every exported image to its Photograph, Side, Asset, role at export time, and derivation lineage.
_Avoid_: Index, metadata file
