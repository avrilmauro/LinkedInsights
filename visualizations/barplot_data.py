"""
This file produces the file: linkedin_skills_df.csv used for the barplot (D3)
"""
import pandas as pd

# read data
df = pd.read_csv("linkedin_df.csv")

# define salary buckets
salary_buckets = [
    { "min": 0, "max": 60000, "label": "Under $60k" },
    { "min": 60001, "max": 85000, "label": "$60k-$85k" },
    { "min": 85001, "max": 110000, "label": "$85k-$110k" },
    { "min": 110001, "max": 150000, "label": "$110k-$150k" },
    { "min": 150001, "max": 200000, "label": "$150k-$200k" },
    { "min": 200001, "max": float("inf"), "label": "$200k+" }
]

# helper function to transform salary bucket
def assign_salary_bucket(salary):
    for bucket in salary_buckets:
        if bucket["min"] <= salary <= bucket["max"]:
            return bucket["label"]
    return "Unknown"

# apply to df
df["salary_bucket"] = df["normalized_salary"].apply(assign_salary_bucket)

# explode skills list
exploded = df.explode('skill_name')
exploded = exploded[exploded.skill_name != 'Other']

# group and count skills by salary bucket
skill_counts = exploded.groupby(['salary_bucket', 'skill_name']).size().reset_index(name='count')

# identify top 5 skills per salary bucket
top5_skills = (
    skill_counts.sort_values(['salary_bucket', 'count'], ascending=[True, False])
    .groupby('salary_bucket')
    .head(5)
)

# export and display
top5_skills.to_csv('linkedin_skills_df.csv')
print(top5_skills)