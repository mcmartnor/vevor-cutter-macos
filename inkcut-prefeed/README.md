# inkcut-prefeed

Material pre-feed and feed-past-cut for roll-fed cutters. Not a
standalone file: this feature is a set of changes to Inkcut's device
engine and job model, shipped as patches.

What it does:

- **Pre-feed**: before cutting, the media is slowly fed out to the
  job's full length (plus the feed-past margin) and back, in host-paced
  10 mm steps. Rolls that would otherwise drag or slip at full machine
  speed mid-cut ("spooling") are unrolled gently first. Pausable and
  cancellable between steps.
- **Feed past cut**: each job ends with the media fed 15 mm past the
  last cut, and the origin is advanced, so the next job starts on fresh
  material without rewinding over finished cuts.

Apply from this repository (see `patches/README.md`):

- `patches/device-plugin.py.patch` — pre-feed step generation
  (origin-relative, bounding-box height), pacing, pause/cancel checks,
  velocity precedence, flush integration
- `patches/job-models.py.patch` — feed-to-end handling and settings
  inheritance in the job model
