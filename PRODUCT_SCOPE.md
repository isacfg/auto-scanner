# Auto Scanner — Product Scope

## Product goal

Digitize loose printed photographs quickly on iPhone without requiring a capture button, synchronize the same library with a native macOS app, and create optional AI-restored versions on the Mac.

The original capture is immutable. Cropped masters and restored images are derived versions and never overwrite it.

## iPhone capture session

The app automatically captures a photograph after confirming:

- document edges;
- camera and photograph stability;
- acceptable focus and exposure;
- absence of strong glare or obstruction;
- the photograph has not already been captured.

After capture, the app provides discreet sound and haptic feedback. The user replaces the photograph and the cycle repeats.

## Back-side capture toggle

Capturing the back is an explicit session-level toggle configured before or during a scanning session. It is off by default. Changing it during a session affects the next photograph that has not started capture; it does not alter a photograph already waiting for its back side.

### Toggle off

1. Capture the front automatically.
2. Complete the photograph immediately.
3. Wait for the next photograph.

### Toggle on

1. Capture the front automatically.
2. Prompt the user to turn the same photograph over.
3. Detect its removal and replacement.
4. Capture the back automatically.
5. Store front and back as one photograph.
6. Wait for the next photograph.

The user can skip the back, redo only one side, or swap sides if classified incorrectly. The back is not sent to restoration by default.

## Stored assets

Each photograph can contain:

- front original;
- front cropped master;
- optional front restored versions;
- optional back original;
- optional back cropped master.

## MVP

### iPhone

- automatic capture without a capture button;
- automatic edge detection, crop, rotation, and perspective correction;
- focus, exposure, glare, shadow, obstruction, and stability quality gates;
- duplicate-capture prevention;
- session photo counter;
- undo, pause, resume, and redo;
- offline capture;
- immutable original and derived cropped master;
- optional linked front-and-back capture controlled by a session toggle;
- basic scanning sessions and deletion of bad captures.

### Synchronization

- one library shared by iPhone and Mac through iCloud/CloudKit;
- resilient background synchronization;
- visible per-photo synchronization state;
- originals, derived assets, and metadata synchronized without destructive conflicts.

### macOS

- native Swift library and session browser;
- manual crop, rotation, and perspective correction;
- front/back viewing and correction;
- asynchronous restoration queue;
- before/after comparison;
- restoration history without overwriting the master;
- export of the front only or front and back together;
- provider metadata, model version, status, parameters, date, and cost per restoration.

## Explicitly out of scope

- album-page scanning;
- multiple photographs captured simultaneously;
- face recognition or grouping;
- duplicate-person discovery;
- decade estimation;
- OCR or handwriting transcription;
- family timelines or family trees;
- collaborative identification of people;
- audio stories;
- slideshows or generated memory videos;
- Apple TV features;
- printing-service integration.
