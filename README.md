### What:

A simple script that scrapes a CurseForge project's dependents (not dependencies) and outputs their **basic public info** to a Json file.

### Why:

Because CurseForge doesn't have any method of searching or sorting through project dependents, plus applying for an API key for simply viewing a projects relations is annoying. Also, as a mod developer, I'd like to know what modpacks include my projects and where my downloads come from.

### How:

This script uses [Selenium's](https://pypi.org/project/selenium/) FireFox web driver to scrape a project's dependents, then outputs those projects as a Json file. `md_converter.py` can then be used to parse the Json file as a Markdown Table.

### Usage:

Argparse is used to specify arguments to the script.  
**Make sure you have FireFox installed for Selenium to use.**

`-p` is required and you must have at least `-j` or `-m` or both.  

| Argument | Meaning                         |       Example |
|:--------:|:--------------------------------|---------------|
|    -p    | Project Slug (found in url)     |  the-aurorian |
|    -j    | (Optional) Output Json file     | ./output.json |
|    -m    | (Optional) Output Markdown file |   ./output.md |
