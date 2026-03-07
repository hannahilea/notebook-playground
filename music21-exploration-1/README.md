# `music21-exploration-1`

In service of blog post https://hannahilea.com/blog/counting-flute-notes/

## Dev log

### Notebook 1: 'gaubert_exploration.ipynb'

- Goal 1: Save jupyter notebook as website (static)
    - Try Quarto! 
- Goal 2: Use music21 to count the number of notes in one flute solo

- Set up:
    ```
    mkdir notebook1
    cd notebook1

    uv init
    uv add music21
    ```

    Configured music21:
    - In terminal, did `uv run python`.
    - Did `from music21 import *`, then `configure.run()`, then followed steps.
    ...this generates a config file that uses musescore as the backend for generating output scores.

    Start notebook:
    ```
    uv run --with jupyter jupyter lab
    ```
    ...then browser opens.

- Okay. Exploration done in that document.

- Next step: Quarto!
- Followed https://quarto.org/docs/get-started/
    - well, actually did `brew install --cask quarto`
    - I use VSCode, so installed extension https://marketplace.visualstudio.com/items?itemName=quarto.quarto 
    - There's a converter for going between jupyter notebooks automatically: `quarto convert basics-jupyter.ipynb`
- Let's do that. From within the notebook1 directory, did `quarto convert gaubert_exploration.ipynb`
    - ...actually scratch that! We can get it to do markdown or html the same way. Let's do markdown to copy it over into my blog!
    ```
    quarto render gaubert_exploration.ipynb --to markdown
    ```
    - This generated gauber_exploration.md AND dir gaubert_exploration_files/ which contains image outputs and that's it.

    - Good to know that it uses the title of the blog post!

    - Copying those over to my blog now.

### Notebook 2: 'concert_count.ipynb'

- Using same uv environment

- Copied first notebook, then deleted most of it 

- Includes some commented-out visualization of score, used for sanity-checking

- Prep it for blog: `quarto render concert_count.ipynb --to markdown`
    ...and copy stuff over
