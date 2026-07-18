# Auto Scanner Domain Glossary

The Auto Scanner domain describes a private library of physical photographs and the digital assets derived from capturing them.

## Library

**Library**:
The user's collection of Photographs, their Sides, Assets, and processing state shared between the iPhone and Mac apps.

**Capture Session**:
A continuous period in which a user digitizes multiple Photographs on the iPhone.

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

**Current Asset**:
The active Original or Master selected for a Side; older lineages may remain as history but are not current.
_Avoid_: Latest asset

**Superseded Asset**:
An Asset retained as history after another Asset becomes current in the same role.
_Avoid_: Deleted asset
