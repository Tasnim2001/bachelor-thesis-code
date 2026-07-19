# Influence of GenAI Adoption on Social Media Text Length

This repository contains the analysis code for my bachelor’s thesis:

**Influence of GenAI Adoption on Social Media Text Length**  
**Tasnim Barakat**  
Ruhr University Bochum, 2026

## Overview

The thesis investigates how text length and writing behavior changed in the subreddit `r/DecidingToBeBetter` before and after the public release of ChatGPT.

The analysis is based on Reddit submissions and comments published between 2019 and 2024. It examines changes in text length, the writing behavior and interaction patterns of active users, post engagement, and differences between original Reddit posts and ChatGPT-generated paraphrases.

## Analysis Workflow

After filtering and preprocessing the raw Reddit datasets, the analysis was conducted in the following order:

### 1. Text Length Analysis
First, the text length of submissions and comments was compared before and after the public release of ChatGPT in late 2022.

### 2. User Communication Network Analysis

Next, the user communication network analysis was conducted.

This part included:

- identifying active users based on their total number of submissions and comments
- comparing the median content length of active users before 2023 and from 2023 onward
- building an interaction network between active users


### 3. Engagement Analysis

The third part examined the engagement received by submissions written by active users.

Engagement was calculated as:

```text
engagement = post score + number of comments
```
The engagement values before 2023 and from 2023 onward were compared. In addition, the relationship between post length and engagement was analyzed using Pearson’s correlation coefficient, and Welch’s independent-samples t-test was used to compare mean engagement between the two periods.

Because some posts had unusually high engagement values, the analysis was repeated after removing upper outliers using the interquartile range (IQR) method.

### 4. Textual Paraphrasing Using ChatGPT

Finally, a paraphrasing experiment was conducted using Reddit submissions published before 2023.
The paraphrasing experiment consists of three separate scripts:

- `chatGpt_text.py`: creates the empty rewriting template
- `chatGpt-rewrite-before-preprocessing.py`: performs an initial word-count analysis of the rewritten texts
- `chatGPT_analysis_with_tokens.py`: performs the final token-based analysis reported in the thesis

The selected posts were divided into three length groups:

- short
- medium
- long

Thirty posts were randomly selected from each group. Each post was then paraphrased three times using ChatGPT with a fixed prompt.

After preprocessing the original and rewritten texts, their token counts were compared:

- overall
- by length group
- by rewritten version


The script `chatGpt_text.py` was used only once to select the 90 posts and create the empty rewriting template. It should not be run again after the rewritten texts have been added manually, because it overwrites `rewrite_90_posts_template.csv`.


## Raw Data

The raw and cleaned Reddit datasets are available in the repository's Releases section.

Files:
- `DecidingToBeBetter_comments_full.csv`
- `DecidingToBeBetter_submissionsNEW.csv`
- `DecidingToBeBetter_comments_cleanedd.csv`
- `DecidingToBeBetter_submissions_cleaned.csv`

Download the required files and place them in the same folder as the Python scripts before running the analysis scripts.

The raw datasets are required for:
- `analysis_comments.py`
- `analysis_submissions.py`
- `user_analysis.py`

All other analysis scripts use the cleaned datasets.

The script `tocsv.py` documents the conversion process from `.zst` files to CSV format.

## Figures

The `images` folder contains all figures included in the thesis.

## Requirements

The analysis was tested with Python 3.13 and requires the following libraries:

- pandas
- matplotlib
- scipy
- networkx