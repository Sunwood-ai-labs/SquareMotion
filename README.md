---
title: Github-Actions-DEMO
emoji: 🌟
colorFrom: green
colorTo: red
sdk: gradio
sdk_version: 3.41.2
app_file: app.py
pinned: false
license: apache-2.0
---


# Github-Actions-DEMO

## run.yaml

[.github\workflows\run.yaml](.github\workflows\run.yaml)

```yaml

name: Sync to Hugging Face hub
on:
  push:
    branches: [main]

  # to run this workflow manually from the Actions tab
  workflow_dispatch:

jobs:
  sync-to-hub:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          lfs: true
      - name: Push to hub
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: git push --force https://MakiAi:$HF_TOKEN@huggingface.co/spaces/MakiAi/Github-Actions-DEMO main

```


## token

![token](image/token.png)