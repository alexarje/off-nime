#!/bin/sh
# OCR the scanned SBCM volumes (1994–1998), which have no text layer: download each volume, render
# its pages, read them with tesseract (Portuguese and English; needs the tesseract-ocr-por package), keep the text with form feeds between pages as data/sbcm_text/<year>.txt, and delete the PDF and page images.
set -e
cd "$(dirname "$0")/../data/sbcm_ocr"
B=https://compmus.ime.usp.br/sbcm
for pair in 1998:1998/SBCM1998Proceedings.pdf 1997:1997/Anais-SBCM-1997.pdf 1995:1995/SBCM1995Proceedings.pdf 1994:1994/SBCM1994Proceedings.pdf; do
  y=${pair%%:*}; f=${pair#*:}
  out=../sbcm_text/$y.txt
  [ -s "$out" ] && [ "$(wc -c < "$out")" -gt 10000 ] && continue
  curl -sL -o vol.pdf "$B/$f"
  rm -rf pages && mkdir pages
  pdftoppm -r 200 -gray vol.pdf pages/p
  : > "$out.tmp"
  for img in pages/p-*.pgm; do
    tesseract "$img" - -l por+eng 2>/dev/null >> "$out.tmp" || true
    printf '\f' >> "$out.tmp"
  done
  mv "$out.tmp" "$out"
  rm -rf pages vol.pdf
  echo "$y done: $(tr -cd '\f' < "$out" | wc -c) pages"
done
