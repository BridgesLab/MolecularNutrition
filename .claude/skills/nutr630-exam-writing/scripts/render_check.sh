#!/bin/bash
# Export .docx files to PDF through Microsoft Word (LibreOffice is not installed on this Mac),
# then compare pagination between an exam and its key.
# Word's sandbox cannot open files in /tmp, so each .docx is staged in ~/Documents/_word_render_tmp,
# exported there, and the PDF is moved to OUTDIR.
#
# Usage: render_check.sh OUTDIR exam.docx [key.docx]
#   - writes OUTDIR/<name>.pdf and page images OUTDIR/<name>-NN.jpg (read them to eyeball layout)
#   - with a key, reports per-page whether text matches once the arrows are removed
set -euo pipefail
OUT="$1"; shift
mkdir -p "$OUT"
STAGE="$HOME/Documents/_word_render_tmp"; mkdir -p "$STAGE"
for f in "$@"; do
  base="$(basename "$f" .docx)"; cp "$f" "$STAGE/$base.docx"; f="$STAGE/$base.docx"; tmp="$STAGE/$base.pdf"
  osascript <<EOF
tell application "Microsoft Word"
  open file name "$f"
  delay 2
  save as active document file name "$tmp" file format format PDF
  close active document saving no
end tell
EOF
  mv "$tmp" "$OUT/$base.pdf"; rm -f "$f"
  echo "$base: $(pdfinfo "$OUT/$base.pdf" | grep Pages)"
  pdftoppm -jpeg -r 60 "$OUT/$base.pdf" "$OUT/$base"
done
if [ $# -eq 2 ]; then
  a="$OUT/$(basename "$1" .docx).pdf"; b="$OUT/$(basename "$2" .docx).pdf"
  n=$(pdfinfo "$a" | awk '/Pages/{print $2}')
  for i in $(seq 1 "$n"); do
    x=$(pdftotext -f $i -l $i "$a" - | tr -d ' \n'); y=$(pdftotext -f $i -l $i "$b" - | sed 's/→//g' | tr -d ' \n')
    [ "$x" = "$y" ] && printf "p%s ok  " "$i" || printf "p%s DIFF  " "$i"
  done; echo
fi
