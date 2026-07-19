"""
Preprocessing and initial analysis of Reddit comments.

Input:
DecidingToBeBetter_comments_full.csv

Steps:
- Load the comments dataset in chunks.
- Remove comments with missing or empty text.
- Remove deleted or removed comments.
- Replace URLs with the token <URL>.
- Calculate the word count for each comment.
- Remove comments with 5 words or fewer.
- Convert the creation date into datetime format.
- Extract the publication year.
- Combine all cleaned chunks into one dataset.
- Restrict the dataset to the analysis period 2019–2024.
- Calculate the median word count per year.
- Save the cleaned comments dataset.

Output:
DecidingToBeBetter_comments_cleanedd.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
file_path = "DecidingToBeBetter_comments_full.csv"
chunk_size = 5000

all_chunks = []
original_count = 0

for chunk in pd.read_csv(file_path, chunksize=chunk_size):
    original_count += len(chunk)

    # remove empty comments
    chunk = chunk.dropna(subset=["body"])
    chunk = chunk[chunk["body"].str.strip() != ""]

    # remove deleted or removed comments
    chunk = chunk[
        ~chunk["body"].isin(["[deleted]", "[removed]"])
    ].copy()

    # replace links with <URL>
    chunk["body"] = chunk["body"].str.replace(
        r"http\S+|www\S+",
        "<URL>",
        regex=True
    )

    # count words
    chunk["word_count"] = chunk["body"].str.split().str.len()

    # remove comments with 5 words or fewer
    chunk = chunk[chunk["word_count"] > 5].copy()

    # convert date and extract year
    chunk["created"] = pd.to_datetime(chunk["created"])
    chunk["year"] = chunk["created"].dt.year

    all_chunks.append(chunk)

# combine all cleaned chunks
df_all_cleaned = pd.concat(all_chunks, ignore_index=True)

# count cleaned comments before restricting the years
cleaned_count_all_years = len(df_all_cleaned)

# restrict to the analysis period used in the thesis
df = df_all_cleaned[
    (df_all_cleaned["year"] >= 2019) &
    (df_all_cleaned["year"] <= 2024)
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
plt.grid(True, alpha=0.3)


plt.show()
print(median_words_per_year)

print("Original comments:", original_count)
print("Cleaned comments all years:", cleaned_count_all_years)
print("Cleaned comments 2019-2024:", len(df))

df.to_csv(
    "DecidingToBeBetter_comments_cleanedd.csv",
    index=False
)