"""
Initial word-count analysis of original and ChatGPT-rewritten Reddit posts.

Input:
rewrite_90_posts_analyzed_with_prompt.csv

Steps:
- Load the dataset containing the original posts and the ChatGPT rewritten versions.
- Check the dataset structure and whether rewritten texts are missing.
- Compare the average word count of original and rewritten texts overall.
- Calculate the mean word count difference between original and rewritten texts.
- Group the results by length group: short, medium, and long.


The final token-based analysis reported in the thesis is performed in chatGPT_analysis_with_tokens.py.

"""
import pandas as pd

df = pd.read_csv(
    "rewrite_90_posts_analyzed_with_prompt.csv",
    encoding="utf-8-sig",
    sep=None,
    engine="python"
)

print(df.columns)
print("Rows:", len(df))
print("Empty texts:", df["text"].isna().sum())


print("\nOverall comparison")
print("Original mean:", df["original_word_count"].mean())
print("Rewritten mean:", df["word_count"].mean())
print("Mean difference:", df["word_count_difference"].mean())

print("\nBy length group")
group_results = df.groupby("length_group").agg(
    original_mean=("original_word_count", "mean"),
    rewritten_mean=("word_count", "mean"),
    mean_difference=("word_count_difference", "mean")
)

print(group_results)
