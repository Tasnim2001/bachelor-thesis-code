"""
Engagement analysis of active-user submissions.

Input:
DecidingToBeBetter_comments_cleanedd.csv
DecidingToBeBetter_submissions_cleaned.csv
user_activity.csv

Steps:
- Load the cleaned comments and submissions datasets.
- Load the user activity table from the active-user analysis.
- Select active users with at least 35 total activities.
- Extract Reddit post IDs from submissions and comments.
- Count how many comments each submission received.
- Add the comment count to the corresponding submission.
- Calculate engagement as Reddit score plus number of comments.
- Keep only submissions written by active users.
- Split the data into two periods: before 2023 and from 2023 onward.
- Compare engagement values between the two periods.
- Calculate the correlation between post length and engagement.
- Use Welch’s independent-samples t-test to compare mean engagement between the period before 2023 and the period from 2023 onward.
- Identify unusually high engagement values using the IQR method.
- Remove posts above the upper outlier limit.
- Repeat the mean, correlation, and t-test analysis without outliers.

"""



import pandas as pd
from scipy.stats import pearsonr, ttest_ind
import matplotlib.pyplot as plt


# load cleaned comments and posts
comments = pd.read_csv(
    "DecidingToBeBetter_comments_cleanedd.csv"
)

submissions = pd.read_csv(
    "DecidingToBeBetter_submissions_cleaned.csv"
)


# load user activity table from the previous analysis
user_activity = pd.read_csv(
    "user_activity.csv"
)


# select the active users again
active_users = user_activity[
    user_activity["total_activity"] >= 35
]["author"]

print("Active users:", len(active_users))


# prepare dates
submissions["created"] = pd.to_datetime(
    submissions["created"]
)

submissions["year"] = submissions["created"].dt.year


# extract post id from submission link
submissions["post_id"] = submissions["link"].str.extract(
    r"/comments/([^/]+)"
)


# extract post id from comment link_id
comments["post_id"] = comments["link_id"].str.replace(
    "t3_",
    "",
    regex=False
)


# count how many comments each post received
comment_count_per_post = (
    comments
    .groupby("post_id")
    .size()
    .reset_index(name="num_comments")
)


# add the number of comments to each post
posts_engagement = submissions.merge(
    comment_count_per_post,
    on="post_id",
    how="left"
)


# posts without comments get zero
posts_engagement["num_comments"] = (
    posts_engagement["num_comments"]
    .fillna(0)
)


# calculate engagement
# engagement = Reddit score + number of comments
posts_engagement["engagement"] = (
    posts_engagement["score"]
    + posts_engagement["num_comments"]
)


# keep only posts written by active users
active_posts_engagement = posts_engagement[
    posts_engagement["author"].isin(active_users)
].copy()


# split posts into before 2023 and from 2023 onward 
engagement_before = active_posts_engagement[
    active_posts_engagement["year"] < 2023
].copy()

engagement_after = active_posts_engagement[
    active_posts_engagement["year"] >= 2023
].copy()


print("\nEngagement analysis")
print("Posts before 2023:", len(engagement_before))
print("Posts from 2023 onward:", len(engagement_after))


# describe engagement values
print("\nEngagement before 2023:")
print(engagement_before["engagement"].describe())

print("\nEngagement from 2023 onward:")
print(engagement_after["engagement"].describe())


# calculate mean engagement
mean_before = engagement_before["engagement"].mean()
mean_after = engagement_after["engagement"].mean()

print("\nMean engagement before 2023:", mean_before)
print("Mean engagement from 2023 onward:", mean_after)


# correlation between post length and engagement
corr_before, p_corr_before = pearsonr(
    engagement_before["word_count"],
    engagement_before["engagement"]
)

corr_after, p_corr_after = pearsonr(
    engagement_after["word_count"],
    engagement_after["engagement"]
)

print("\nCorrelation between post length and engagement")
print("Before 2023:", corr_before)
print("p-value before 2023:", p_corr_before)

print("From 2023 onward:", corr_after)
print("p-value from 2023 onward:", p_corr_after)


#  Test whether mean engagement differs between the two periods
t_stat, p_value = ttest_ind(
    engagement_before["engagement"],
    engagement_after["engagement"],
    equal_var=False
)

print("\nT-test for mean engagement")
print("t-statistic:", t_stat)
print("p-value:", p_value)



#### Outlier analysis ###


# calculate the IQR threshold using engagement values from both periods
q1 = active_posts_engagement["engagement"].quantile(0.25)
q3 = active_posts_engagement["engagement"].quantile(0.75)

iqr = q3 - q1

# values above this limit are treated as outliers
upper_limit = q3 + 1.5 * iqr

print("\nOutlier limit:", upper_limit)


# find outlier posts
engagement_outliers = active_posts_engagement[
    active_posts_engagement["engagement"] > upper_limit
]

print("Number of outliers:", len(engagement_outliers))


# remove outliers
engagement_clean = active_posts_engagement[
    active_posts_engagement["engagement"] <= upper_limit
].copy()


# split the cleaned data again
engagement_before_clean = engagement_clean[
    engagement_clean["year"] < 2023
].copy()

engagement_after_clean = engagement_clean[
    engagement_clean["year"] >= 2023
].copy()


print("\nPosts without outliers")
print("Before 2023:", len(engagement_before_clean))
print("From 2023 onward:", len(engagement_after_clean))


# mean engagement after removing outliers
mean_before_clean = engagement_before_clean["engagement"].mean()
mean_after_clean = engagement_after_clean["engagement"].mean()

print("\nMean engagement without outliers")
print("Before 2023:", mean_before_clean)
print("From 2023 onward:", mean_after_clean)


### Figure mean engagement with/without outliers ###

labels = [
    "Before 2023\nwith outliers",
    "Before 2023\nwithout outliers",
    "After 2023\nwith outliers",
    "After 2023\nwithout outliers"
]

values = [
    mean_before,
    mean_before_clean,
    mean_after,
    mean_after_clean
]

plt.figure(figsize=(10, 6))

plt.bar(labels, values)

plt.ylabel("Mean engagement")

plt.show()
# correlation after removing outliers
corr_before_clean, p_corr_before_clean = pearsonr(
    engagement_before_clean["word_count"],
    engagement_before_clean["engagement"]
)

corr_after_clean, p_corr_after_clean = pearsonr(
    engagement_after_clean["word_count"],
    engagement_after_clean["engagement"]
)

print("\nCorrelation without outliers")
print("Before 2023:", corr_before_clean)
print("p-value before 2023:", p_corr_before_clean)

print("From 2023 onward:", corr_after_clean)
print("p-value from 2023 onward:", p_corr_after_clean)


# t-test after removing outliers
t_stat_clean, p_value_clean = ttest_ind(
    engagement_before_clean["engagement"],
    engagement_after_clean["engagement"],
    equal_var=False
)

print("\nT-test without outliers")
print("t-statistic:", t_stat_clean)
print("p-value:", p_value_clean)
