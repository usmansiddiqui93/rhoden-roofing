#!/usr/bin/env bash
# Copies every rhodenroofing.com image into ./images and rewrites index.html to use them.
set -e
mkdir -p images
grep -oE 'https://rhodenroofing\.com/wp-content/uploads/[^"]+\.(png|jpg|jpeg)' index.html | sort -u | while read -r url; do
  f="images/$(basename "$url")"
  [ -f "$f" ] || curl -sSL "$url" -o "$f"
  sed -i.bak "s#${url}#${f}#g" index.html
done
rm -f index.html.bak
echo "Done - images saved in ./images"
