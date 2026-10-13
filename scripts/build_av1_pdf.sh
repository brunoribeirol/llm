#!/bin/sh
# Render the AV1 dossier (av1/final/*.html) to PDF with headless Chrome.
#
# Run from the repository root, outside the agent sandbox:  scripts/build_av1_pdf.sh
#
# Headless Chrome writes the PDF within a few seconds but does not always exit on its own,
# so this script waits for the file and then stops the browser itself.
set -eu

SRC="$PWD/av1/final/avaliacao01_bruno_ribeiro.html"
OUT="$PWD/av1/final/avaliacao01_bruno_ribeiro.pdf"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

[ -f "$SRC" ] || { echo "missing $SRC (run from the repository root)" >&2; exit 1; }
[ -x "$CHROME" ] || { echo "Google Chrome not found at $CHROME" >&2; exit 1; }

# A throwaway profile keeps this run apart from any Chrome window that is already open.
PROFILE="$(mktemp -d "${TMPDIR:-/tmp}/chrome-av1.XXXXXX")"
rm -f "$OUT"

"$CHROME" --headless=new --no-first-run --no-pdf-header-footer \
  --user-data-dir="$PROFILE" --print-to-pdf="$OUT" "file://$SRC" >/dev/null 2>&1 &
CHROME_PID=$!

# Wait up to 30 seconds for the PDF to appear, then give Chrome a moment to finish writing.
i=0
while [ ! -s "$OUT" ] && [ "$i" -lt 30 ]; do
  sleep 1
  i=$((i + 1))
done
sleep 2
kill "$CHROME_PID" 2>/dev/null || true
wait "$CHROME_PID" 2>/dev/null || true
# Chrome helpers may still be writing to the profile; a leftover temp folder is harmless.
rm -rf "$PROFILE" 2>/dev/null || true

[ -s "$OUT" ] || { echo "PDF was not generated" >&2; exit 1; }
echo "wrote $OUT"
command -v pdfinfo >/dev/null 2>&1 && pdfinfo "$OUT" | grep -E '^Pages'
exit 0
