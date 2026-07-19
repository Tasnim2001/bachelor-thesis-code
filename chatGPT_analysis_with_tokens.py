"""
Token-based comparison of original and ChatGPT-rewritten Reddit posts.

Input:
rewrite_90_posts_analyzed_with_prompt - Kopie.csv

Steps:
- Load the dataset containing the original posts and rewritten texts.
- Preprocess original and rewritten texts using the same tokenization method.
- Convert text to lowercase.
- Remove URL placeholders and web links.
- Extract words, numbers, and apostrophes inside words as tokens.
- Calculate token counts for original and rewritten texts.
- Calculate the token count difference between rewritten and original texts.
- Compare token counts overall, by length group, and by rewritten version.

Output:
rewrite_90_posts_with_token.csv

"""

import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv(
    "rewrite_90_posts_analyzed_with_prompt - Kopie.csv",
    encoding="utf-8-sig",
    sep=None,
    engine="python"
)

print(df.columns)


def preprocess_and_tokenize(text):
    if pd.isna(text):
        return []

    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"<url>|http\S+|www\S+", " ", text)

    # Keep words, numbers, and apostrophes inside words
    # Examples kept as one token: don't, i'm, it's
    tokens = re.findall(r"[a-zA-Z0-9]+(?:'[a-zA-Z0-9]+)?", text)

    return tokens


# Change "original_text" if the column has another name
df["original_token_count"] = df["original_text"].apply(
    lambda x: len(preprocess_and_tokenize(x))
)

df["rewritten_token_count"] = df["text"].apply(
    lambda x: len(preprocess_and_tokenize(x))
)

df["token_count_difference"] = (
    df["rewritten_token_count"] - df["original_token_count"]
)

print("\nOverall comparison after preprocessing")
print("Original mean:", round(df["original_token_count"].mean(), 2))
print("Rewritten mean:", round(df["rewritten_token_count"].mean(), 2))
print("Mean difference:", round(df["token_count_difference"].mean(), 2))

print("\nBy length group after preprocessing")
group_results = df.groupby("length_group").agg(
    original_mean=("original_token_count", "mean"),
    rewritten_mean=("rewritten_token_count", "mean"),
    mean_difference=("token_count_difference", "mean")
)


group_order = ["Short", "Medium", "Long"]
plot_data = group_results.reindex(group_order)

x = np.arange(len(group_order))
width = 0.35

plt.figure(figsize=(10, 6))

plt.bar(
    x - width / 2,
    plot_data["original_mean"],
    width,
    label="Original"
)

plt.bar(
    x + width / 2,
    plot_data["rewritten_mean"],
    width,
    label="Rewritten"
)

plt.xticks(x, group_order)
plt.ylabel("Mean token count")
plt.legend(loc="upper left")



plt.show()
print(group_results.round(2).to_string())

print("\nBy version after preprocessing")
version_results = df.groupby("version").agg(
    original_mean=("original_token_count", "mean"),
    rewritten_mean=("rewritten_token_count", "mean"),
    mean_difference=("token_count_difference", "mean")
)

print(version_results.round(2).to_string())

# rename the column 
df = df.rename(columns={"text": "rewritten_text"})

df.to_csv(
    "rewrite_90_posts_with_token.csv",
    index=False,
    encoding="utf-8-sig"
)


