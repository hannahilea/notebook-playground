#!/bin/bash

filename=$1
notebook_name="$(basename ${filename%.*})"
echo "Tidying $filename (notebook name '${notebook_name}')"

cat $filename \
| sed -E "s/ execution_count=\"[0-9]+\"//" \
| sed -E "s/${notebook_name}_files\/figure-markdown/.\/assets/" \
| sed -E "s/        //" \
> $filename.clean.md
