
"""
Active user and interaction network analysis.

Input:
DecidingToBeBetter_comments_full.csv
DecidingToBeBetter_submissionsNew.csv
DecidingToBeBetter_comments_cleanedd.csv
DecidingToBeBetter_submissions_cleaned.csv

Steps:
- Load raw comments and submissions to measure overall user activity.
- Convert creation dates into datetime format and extract publication years.
- Restrict the raw datasets to the analysis period 2019-2024.
- Remove deleted, moderator, and other invalid authors.
- Count comments and submissions per user.
- Calculate total activity as comments plus submissions.
- Select active users with at least 35 activities.
- Use the cleaned datasets to compare median comment and post length before 2023 and from 2023 onward.
- Extract Reddit post IDs and match active-user comments to active-user submissions.
- Remove self-comments.
- Build a directed interaction network where edges represent comments from one active user to another active user's post.
- Save user activity, network overview, and interaction edge list.

Output:
user_activity.csv
network_overview.csv
interaction_edges.csv
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Replace these paths if the raw CSV files have different names.
comments_raw = pd.read_csv("DecidingToBeBetter_comments_full.csv")
submissions_raw = pd.read_csv("DecidingToBeBetter_submissionsNew.csv")

comments = pd.read_csv(
    "DecidingToBeBetter_comments_cleanedd.csv"
)

submissions = pd.read_csv(
    "DecidingToBeBetter_submissions_cleaned.csv"
)

comments_raw["created"] = pd.to_datetime(comments_raw["created"])
comments_raw["year"] = comments_raw["created"].dt.year

submissions_raw["created"] = pd.to_datetime(submissions_raw["created"])
submissions_raw["year"] = submissions_raw["created"].dt.year

# keep only 2019-2024 in both datasets
comments_raw = comments_raw[
    (comments_raw["year"] >= 2019)
    & (comments_raw["year"] <= 2024)
]

submissions_raw = submissions_raw[
    (submissions_raw["year"] >= 2019)
    & (submissions_raw["year"] <= 2024)
]

# remove invalid authors
invalid_authors = [
    "[deleted]",
    "u/[deleted]",
    "AutoModerator",
    "u/AutoModerator",
    "DecidingToBeBetter-ModTeam",
    "u/DecidingToBeBetter-ModTeam"
]

comments_raw = comments_raw[~comments_raw["author"].isin(invalid_authors)]
submissions_raw = submissions_raw[~submissions_raw["author"].isin(invalid_authors)]

##### count activity = comments + submissions ######

# count comments  and posts per user
comment_counts = comments_raw["author"].value_counts().rename("n_comments")
submission_counts = submissions_raw["author"].value_counts().rename("n_submissions")

# combine both counts into one table
user_activity = pd.concat(
    [comment_counts, submission_counts],
    axis=1
).fillna(0)

# total activity = comments + submissions
user_activity["total_activity"] = (
    user_activity["n_comments"] + user_activity["n_submissions"]
)
# sort users from most active to least active
user_activity = user_activity.sort_values(
    "total_activity",
    ascending=False
)

print(user_activity["total_activity"].describe())

activity_quantiles = user_activity["total_activity"].quantile([
    0.50,
    0.75,
    0.90,
    0.95,
    0.99
])

print(activity_quantiles)

# number of users above different activity thresholds

users_35 = len(
    user_activity[
        user_activity["total_activity"] >= 35
    ]
)

users_50 = len(
    user_activity[
        user_activity["total_activity"] >= 50
    ]
)

users_100 = len(
    user_activity[
        user_activity["total_activity"] >= 100
    ]
)

print("Users >=35:", users_35)
print("Users >=50:", users_50)
print("Users >=100:", users_100)


### User distribution graph ###
plt.figure(figsize=(8, 5))

plt.hist(
    user_activity["total_activity"],
    bins=60
)

plt.yscale("log")
plt.axvline(
    35,
    color="red",
    linestyle="--",
    linewidth=1.5,
    label=f"35 activities ({users_35} users)"
)

plt.axvline(
    50,
    color="red",
    linestyle=":",
    linewidth=1.5,
    label=f"50 activities ({users_50} users)"
)

plt.axvline(
    100,
    color="red",
    linestyle="-.",
    linewidth=1.5,
    label=f"100 activities ({users_100} users)"
)
plt.xlabel("Total activity (comments + submissions)")
plt.ylabel("Number of users (log scale)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()



##### Median length analysis for posts and comments among active users #####

# select users with at least 35 activities
active_users = user_activity[
    user_activity["total_activity"] >= 35
].index
print("Total active users:", len(active_users))
comments["created"] = pd.to_datetime(
    comments["created"]
)

comments["year"] = comments["created"].dt.year

before_comments = comments[
    (comments["year"] < 2023)
    & (comments["author"].isin(active_users))
]

after_comments = comments[
    (comments["year"] >= 2023)
    & (comments["author"].isin(active_users))
]

# median comment length per user before 2023
before_comment_median = (
    before_comments
    .groupby("author")["word_count"]
    .median()
)
# median comment length per user from 2023 onward
after_comment_median = (
    after_comments
    .groupby("author")["word_count"]
    .median()
)
print("Active users before 2023:",
      before_comments["author"].nunique())

print("Active users from 2023 onward:",
      after_comments["author"].nunique())


# combine before and after median values
comment_change = pd.DataFrame({
    "before_median": before_comment_median,
    "after_median": after_comment_median
}).dropna()

# calculate change in median comment length
comment_change["difference"] = (
    comment_change["after_median"]
    - comment_change["before_median"]
)

#print(comment_change["difference"].describe())
print(
    "Users with comments in both periods:",
    len(comment_change)
)

increased = (
    comment_change["difference"] > 0
).sum()

decreased = (
    comment_change["difference"] < 0
).sum()

unchanged = (
    comment_change["difference"] == 0
).sum()
print("Increased:", increased)
print("Decreased:", decreased)
print("Unchanged:", unchanged)

comment_total = len(comment_change)

comment_increased_pct = increased / comment_total * 100
comment_decreased_pct = decreased / comment_total * 100
comment_unchanged_pct = unchanged / comment_total * 100
comment_median_difference = comment_change["difference"].median()

print("Comment increased %:", comment_increased_pct)
print("Comment decreased %:", comment_decreased_pct)
print("Comment unchanged %:", comment_unchanged_pct)
print("Comment median difference:", comment_median_difference)

# post length analysis for active users


submissions["created"] = pd.to_datetime(
    submissions["created"]
)

submissions["year"] = submissions["created"].dt.year

before_posts = submissions[
    (submissions["year"] < 2023)
    & (submissions["author"].isin(active_users))
]

after_posts = submissions[
    (submissions["year"] >= 2023)
    & (submissions["author"].isin(active_users))
]

before_post_median = (
    before_posts
    .groupby("author")["word_count"]
    .median()
)

after_post_median = (
    after_posts
    .groupby("author")["word_count"]
    .median()
)

print("Active users with posts before 2023:",
      before_posts["author"].nunique())

print("Active users with posts from 2023 onward:",
      after_posts["author"].nunique())

post_change = pd.DataFrame({
    "before_median": before_post_median,
    "after_median": after_post_median
}).dropna()

post_change["difference"] = (
    post_change["after_median"]
    - post_change["before_median"]
)

#print(post_change["difference"].describe())

print(
    "Users with posts in both periods:",
    len(post_change)
)

increased_posts = (
    post_change["difference"] > 0
).sum()

decreased_posts = (
    post_change["difference"] < 0
).sum()

unchanged_posts = (
    post_change["difference"] == 0
).sum()

print("Increased posts:", increased_posts)
print("Decreased posts:", decreased_posts)
print("Unchanged posts:", unchanged_posts)

post_total = len(post_change)

post_increased_pct = increased_posts / post_total * 100
post_decreased_pct = decreased_posts / post_total * 100
post_unchanged_pct = unchanged_posts / post_total * 100
post_median_difference = post_change["difference"].median()

print("Post increased %:", post_increased_pct)
print("Post decreased %:", post_decreased_pct)
print("Post unchanged %:", post_unchanged_pct)
print("Post median difference:", post_median_difference)



###### network interaction preprocessing ######

# extract Reddit post ID from submission URL
submissions["post_id"] = submissions["link"].str.extract(
    r"/comments/([^/]+)"
)


# keep only posts written by active users
active_posts = submissions[
    submissions["author"].isin(active_users)
][["post_id", "author", "created", "year"]].rename(
    columns={
        "author": "post_author",
        "created": "post_created",
        "year": "post_year"
    }
)

# keep only comments written by active users
comments_network = comments[
    comments["author"].isin(active_users)
].copy()

# remove Reddit prefix (t3_) from comment post IDs
comments_network["post_id"] = comments_network["link_id"].str.replace(
    "t3_", "",
    regex=False
)

# rename columns
comments_network = comments_network.rename(
    columns={
        "author": "comment_author",
        "created": "comment_created",
        "year": "comment_year"
    }
)

# match each comment with its corresponding post
interactions = comments_network.merge(
    active_posts,
    on="post_id",
    how="inner"
)

# remove cases where users comment on their own posts
interactions = interactions[
    interactions["comment_author"] != interactions["post_author"]
]


# create interaction pairs:
# comment_author -> post_author
edges = (
    interactions
    .groupby(["comment_author", "post_author"])
    .size()
    .reset_index(name="weight")
)


print("Number of edges:", len(edges))

print("Active users:", len(active_users))
# active users who commented on other users' posts
print("Unique commenters:", edges["comment_author"].nunique())
# Active post authors are counted only if at least one active user commented on their post.
print("Unique post authors:", edges["post_author"].nunique())


### Interaction network of active users ###

# Build directed network:
# comment_author -> post_author
G = nx.from_pandas_edgelist(
    edges,
    source="comment_author",
    target="post_author",
    edge_attr="weight",
    create_using=nx.DiGraph()
)

print("Total active users:", len(active_users))
print("Users in network:", G.number_of_nodes())
print("Network edges:", G.number_of_edges())

network_share = (
    G.number_of_nodes() / len(active_users)
) * 100

print("Share of active users in network:", network_share)

# Save simple overview table
network_overview = pd.DataFrame({
    "Metric": [
        "Active users",
        "Users in network",
        "Interaction edges"
    ],
    "Value": [
        len(active_users),
        G.number_of_nodes(),
        G.number_of_edges()
    ]
})


user_activity.to_csv(
    "user_activity.csv"
)

network_overview.to_csv(
    "network_overview.csv",
    index=False
)

edges.to_csv("interaction_edges.csv", index=False)

