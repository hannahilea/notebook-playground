#!/bin/bash

export OUTFILE=tonuino-birds-of-north-america.yaml

cat >"$OUTFILE" <<EOL
sourcebasedir: "/Users/skye/Downloads/The Cornell Guide to Bird Sounds--United States and Canada (v2025)"
# cardcookie: "1337B347"
# version: 2
# maxcardsperqrcode: 4
# filenametype: "mp3tags"

cards:
EOL

function append_birdsong_files() {
    local I_BIRD="$1"
    local BIRD="$2"

    printf "  $I_BIRD:\n    description: $BIRD\n    source:\n" >> "$OUTFILE"
    cat audio-full-tracklist.txt \
        | grep "$BIRD" \
        | sort \
        | awk '{ print "      - " $0 }' \
        >> "$OUTFILE"
    printf "    mode: party-from-to\n    from_song: 1\n    to_song: "  >> "$OUTFILE"
    cat audio-full-tracklist.txt \
        | grep "$BIRD" \
        | wc -l \
        | tr -d ' ' \
        >> "$OUTFILE"
    printf "\n" >> "$OUTFILE"
}


export i_card=1
while read line; do
    # Skip commented lines
    if [[ (${line:0:1} != \#) && -n $line ]] ; then
        append_birdsong_files "$i_card" "$line"
        let "i_card+=1"
    #else
    # echo "SKIPPED $line"
    fi
done < birds-of-north-america-deck.txt
