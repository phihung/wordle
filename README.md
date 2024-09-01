---
title: Wordle
emoji: 🐢
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: apache-2.0
app_port: 5001
---

# Wordle

I created a Wordle clone using [FastHTML](https://fastht.ml/) and Tailwind CSS.

You can play it live here: https://phihung-wordle.hf.space

Check out my [Github](https://github.com/phihung/wordle) repository

## Run

```bash
uv sync
python src/wordle/ui.py
```

To run the project using Docker:

```bash
docker build -t wordle .
docker run --rm -p 5001:5001 -it wordle
```

## Credits

Some of the Tailwind CSS code is inspired by: [MahmoudFettal/wordle](https://github.com/MahmoudFettal/wordle)
