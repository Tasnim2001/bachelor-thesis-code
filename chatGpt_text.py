"""
Creates the initial template for the ChatGPT rewriting experiment.

IMPORTANT:
This script is not part of the final analysis workflow.

It was used only once to select the 90 Reddit posts and create the empty file
`rewrite_90_posts_template.csv` before the rewritten texts were added manually.

Do not run this script again after the rewritten texts have been entered,
because the existing template file will be overwritten.

Input:
DecidingToBeBetter_submissions_cleaned.csv

Output:
rewrite_90_posts_template.csv
"""


# WARNING:
# This overwrites the existing template file.
# Do not run it.

import pandas as pd

posts = pd.read_csv("DecidingToBeBetter_submissions_cleaned.csv")

pre_chatgpt_posts = posts[posts["year"] < 2023]

q1 = pre_chatgpt_posts["word_count"].quantile(0.33)
q2 = pre_chatgpt_posts["word_count"].quantile(0.66)

print("Short <", q1)
print("Medium:", q1, "-", q2)
print("Long >", q2)

pre_chatgpt_posts["length_group"] = pd.cut(
    pre_chatgpt_posts["word_count"],
    bins=[0, 109, 236, float("inf")],
    labels=["Short", "Medium", "Long"]
)

print(pre_chatgpt_posts["length_group"].value_counts())
print("Posts before 2023:", len(pre_chatgpt_posts))

short_posts = pre_chatgpt_posts[
    pre_chatgpt_posts["length_group"] == "Short"
].sample(n=30, random_state=42)

medium_posts = pre_chatgpt_posts[
    pre_chatgpt_posts["length_group"] == "Medium"
].sample(n=30, random_state=42)

long_posts = pre_chatgpt_posts[
    pre_chatgpt_posts["length_group"] == "Long"
].sample(n=30, random_state=42)


sample_posts = pd.concat([
    short_posts,
    medium_posts,
    long_posts
])

print(len(sample_posts))


# create simple post id
sample_posts = sample_posts.reset_index(drop=True)
sample_posts["post_id"] = range(1, len(sample_posts) + 1)

# create rows only for rewritten versions
version_1 = sample_posts[
    [
        "post_id",
        "year",
        "length_group",
        "text",
        "word_count"
    ]
].copy()

version_1 = version_1.rename(
    columns={
        "text": "original_text",
        "word_count": "original_word_count"
    }
)

version_1["version"] = "version_1"
version_1["text"] = ""
version_1["word_count"] = ""


version_2 = version_1.copy()
version_2["version"] = "version_2"


version_3 = version_1.copy()
version_3["version"] = "version_3"


rewrite_template_long = pd.concat(
    [
        version_1,
        version_2,
        version_3
    ],
    ignore_index=True
)

version_order = {
    "version_1": 1,
    "version_2": 2,
    "version_3": 3
}

rewrite_template_long["version_order"] = (
    rewrite_template_long["version"].map(version_order)
)

rewrite_template_long = rewrite_template_long.sort_values(
    by=[
        "post_id",
        "version_order"
    ]
)

rewrite_template_long = rewrite_template_long.drop(
    columns=[
        "version_order"
    ]
)

rewrite_template_long = rewrite_template_long[
    [
        "post_id",
        "year",
        "length_group",
        "original_text",
        "original_word_count",
        "version",
        "text",
        "word_count"
    ]
]

rewrite_template_long.to_csv(
    "rewrite_90_posts_template.csv",
    index=False,
    encoding="utf-8-sig"
)

