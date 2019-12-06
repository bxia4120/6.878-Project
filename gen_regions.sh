#!/usr/bin/env bash
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 bin_size"
    exit 1
fi
num=$1
find . -name '*.bigWig' | parallel -j10 "stat {}.done >/dev/null 2>&1 || bwtool summary $num {} /dev/stdout -with-sum -without-median | gzip -c > {.}.$num.bed.gz && touch {}.done"
