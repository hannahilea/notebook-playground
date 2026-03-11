# Notebook playground 

Library of one-off [<img alt="Static Badge" src="https://img.shields.io/badge/&#x1F490;%20Bouquet%20-x?style=flat&amp;label=Project%20type&amp;color=1E1E1D">](https://www.hannahilea.com/blog/houseplant-programming) notebooks and scripts. No promises around quality, useability, reproducibility, or maintenance. :) 

Initially created to support [hannahilea.com/blog](https://hannahilea.com/blog/).

For specifics, see the per-directory `README.md`s. Which might exist! And might even be correct!

## Contents

- 2026-03-05: [music21-exploration-1](./music21-exploration-1)
- 2026-03-08: [tonuino-birds](./tonuino-birds)


## Make new dir

```
export NAME=new-name

mkdir "$NAME"
cd "$NAME"
echo "# `$NAME` >> "README.md"
touch ".gitignore"

# Optional, if python will be involved
uv init --bare
```
