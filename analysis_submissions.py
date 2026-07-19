
"""
Preprocessing and initial analysis of Reddit submissions.

Input:
DecidingToBeBetter_submissionsNew.csv

Steps:
- Load the raw submissions dataset.
- Remove entries with missing or empty text.
- Remove deleted or removed posts.
- Convert the creation date into datetime format.
- Extract the publication year.
- Replace URLs with the token <URL>.
- Calculate the word count for each submission.
- Remove submissions with 10 words or fewer.
- Restrict the dataset to the analysis period 2019-2024.
- Calculate the median word count per year.
- Save the cleaned submissions dataset.

Output:
DecidingToBeBetter_submissions_cleaned.csv
"""

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("DecidingToBeBetter_submissionsNew.csv")
# Count original submissions before preprocessing
original_count = len(df)

# remove empty posts
df = df.dropna(subset=["text"])
df = df[df["text"].str.strip() != ""]

#remove deleted or removed posts
df = df[
    ~df["text"].isin(["[deleted]", "[removed]"])
]

# convert data format
df["created"] = pd.to_datetime(df["created"])
df["year"] = df["created"].dt.year

# check posts per year
print(df["year"].value_counts().sort_index())

# replace links with <URL> 
df["text"] = df["text"].str.replace(
    r"http\S+|www\S+",
    "<URL>",
    regex=True
)
# count word per post
df["word_count"] = df["text"].str.split().str.len()

# remove posts with 10 words or fewer
df = df[df["word_count"] > 10]
cleaned_count_all_years = len(df)
df = df[
    (df["year"] >= 2019)
    & (df["year"] <= 2024)
].copy()

# median word count per year
median_words_per_year = df.groupby("year")["word_count"].median()


plt.figure(figsize=(8, 5))

plt.plot(
    median_words_per_year.index,
    median_words_per_year.values,
    marker="o",
    markersize=7,
    linewidth=2
)
plt.xlabel("Year")
plt.ylabel("Median Word Count")
plt.grid(True)


plt.show()

print(median_words_per_year)
print("Original submissions:", original_count)
print("Cleaned submissions all years:", cleaned_count_all_years)
print("Cleaned submissions 2019-2024:", len(df))

# save cleaned submissions with year and word_count
df.to_csv("DecidingToBeBetter_submissions_cleaned.csv", index=False)
