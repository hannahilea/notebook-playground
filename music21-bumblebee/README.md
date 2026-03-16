# `music21-bumblebee`

In service of blog post https://hannahilea.com/blog/TODO/

Notebooks:
- [./bumblebee.ipynb](./bumblebee.ipynb)

## Dev log

Start notebook:
```
uv run --with jupyter jupyter lab
```

Prep it for blog:

```
quarto render bumblebee.ipynb --to markdown --output-dir x_temp_blog_staging

../tidy-md.sh ../x_temp_blog_staging/bumblebee.md
```



    ...and copy stuff over

- can add `#| output: false` at start of notebook cell

