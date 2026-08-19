# inkcut-pdf-import

Opens PDF and Adobe Illustrator (.ai, PDF-compatible) files directly in
Inkcut: the document is converted to SVG on open and parsed as usual.

- Conversion via poppler's `pdftocairo` (fallback: Inkscape), cached by
  content hash under `~/.config/inkcut/imports/`
- Multi-page PDFs import page 1 and warn (page count via `pdfinfo`)
- Atomic cache writes with unique temp files (safe under concurrent use)
- The original file name/path is what the UI, recent-files menu and job
  history show — not the internal cache path

Installation: copy `importers.py` to `inkcut/job/importers.py`. The
integration (open/convert off the UI thread, drag-and-drop of .pdf/.ai,
`source_document` bookkeeping) lives in the job plugin — apply
`patches/job-plugin.py.patch`, `patches/job-models.py.patch` and
`patches/job-manifest.enaml.patch` (see `patches/README.md`).

Dependencies: `brew install poppler` (provides `pdftocairo` and
`pdfinfo`).
