import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="EduPro Learner Analytics",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 EduPro Learner Demographics & Course Enrollment Analysis")
st.write(
    "Analysis of learner demographics, course preferences and enrollment behavior."
)

# -----------------------------
# Load Dataset
# -----------------------------
file_path = "EduPro Online Platform.xlsx"

users = pd.read_excel(file_path, sheet_name="Users")
courses = pd.read_excel(file_path, sheet_name="Courses")
transactions = pd.read_excel(file_path, sheet_name="Transactions")

# -----------------------------
# Merge Data
# -----------------------------
data = pd.merge(users, transactions, on="UserID")
data = pd.merge(data, courses, on="CourseID")

# -----------------------------
# Create Age Groups
# -----------------------------
def age_group(age):
    if age < 18:
        return "<18"
    elif age <= 25:
        return "18-25"
    elif age <= 35:
        return "26-35"
    elif age <= 45:
        return "36-45"
    else:
        return "45+"

data["AgeGroup"] = data["Age"].apply(age_group)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔎 Filters")

age_filter = st.sidebar.multiselect(
    "Age Group",
    data["AgeGroup"].unique(),
    default=data["AgeGroup"].unique()
)

gender_filter = st.sidebar.multiselect(
    "Gender",
    data["Gender"].unique(),
    default=data["Gender"].unique()
)

category_filter = st.sidebar.multiselect(
    "Course Category",
    data["CourseCategory"].unique(),
    default=data["CourseCategory"].unique()
)

level_filter = st.sidebar.multiselect(
    "Course Level",
    data["CourseLevel"].unique(),
    default=data["CourseLevel"].unique()
)

# -----------------------------
# Apply Filters
# -----------------------------
filtered = data[
    (data["AgeGroup"].isin(age_filter)) &
    (data["Gender"].isin(gender_filter)) &
    (data["CourseCategory"].isin(category_filter)) &
    (data["CourseLevel"].isin(level_filter))
]

# -----------------------------
# KPI SECTION
# -----------------------------
st.header("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Enrollments",
    len(filtered)
)

col2.metric(
    "Total Learners",
    filtered["UserID"].nunique()
)

learner_counts = filtered.groupby("UserID")["CourseID"].count()

col3.metric(
    "Avg Courses per Learner",
    round(learner_counts.mean(), 2) if len(learner_counts) > 0 else 0
)

col4.metric(
    "Popular Category",
    filtered["CourseCategory"].value_counts().idxmax()
    if len(filtered) > 0 else "N/A"
)

# -----------------------------
# DEMOGRAPHIC OVERVIEW
# -----------------------------
st.header("👥 Learner Demographic Overview")

col1, col2 = st.columns(2)

with col1:

    st.subheader("Age Group Distribution")

    age_counts = filtered["AgeGroup"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(7, 4))

    sns.barplot(
        x=age_counts.index,
        y=age_counts.values,
        ax=ax
    )

    ax.set_xlabel("Age Group")
    ax.set_ylabel("Learners")
    ax.set_title("Learners by Age Group")

    st.pyplot(fig)

with col2:

    st.subheader("Gender Participation")

    gender_counts = filtered["Gender"].value_counts()

    fig, ax = plt.subplots(figsize=(7, 4))

    sns.barplot(
        x=gender_counts.index,
        y=gender_counts.values,
        ax=ax
    )

    ax.set_xlabel("Gender")
    ax.set_ylabel("Learners")
    ax.set_title("Gender Distribution")

    st.pyplot(fig)

# -----------------------------
# AGE-WISE ENROLLMENT
# -----------------------------
st.header("📈 Age-wise Enrollment")

age_enrollment = filtered["AgeGroup"].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(10, 5))

sns.barplot(
    x=age_enrollment.index,
    y=age_enrollment.values,
    ax=ax
)

ax.set_xlabel("Age Group")
ax.set_ylabel("Enrollments")
ax.set_title("Enrollments Across Age Groups")

st.pyplot(fig)

# -----------------------------
# COURSE PREFERENCES
# -----------------------------
st.header("📚 Course Preference Analysis")

col1, col2 = st.columns(2)

with col1:

    st.subheader("Course Category Popularity")

    category_counts = filtered["CourseCategory"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.barplot(
        x=category_counts.index,
        y=category_counts.values,
        ax=ax
    )

    ax.set_xlabel("Course Category")
    ax.set_ylabel("Enrollments")
    ax.tick_params(axis="x", rotation=45)

    st.pyplot(fig)

with col2:

    st.subheader("Course Level Preference")

    level_counts = filtered["CourseLevel"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.barplot(
        x=level_counts.index,
        y=level_counts.values,
        ax=ax
    )

    ax.set_xlabel("Course Level")
    ax.set_ylabel("Enrollments")

    st.pyplot(fig)

# -----------------------------
# COURSE TYPE
# -----------------------------
st.subheader("Course Type Popularity")

type_counts = filtered["CourseType"].value_counts()

fig, ax = plt.subplots(figsize=(8, 5))

sns.barplot(
    x=type_counts.index,
    y=type_counts.values,
    ax=ax
)

ax.set_xlabel("Course Type")
ax.set_ylabel("Enrollments")

st.pyplot(fig)

# -----------------------------
# AGE GROUP VS CATEGORY
# -----------------------------
st.header("🔥 Demographic Course Preferences")

st.subheader("Age Group vs Course Category")

age_category = pd.crosstab(
    filtered["AgeGroup"],
    filtered["CourseCategory"]
)

fig, ax = plt.subplots(figsize=(10, 6))

sns.heatmap(
    age_category,
    annot=True,
    fmt="d",
    ax=ax
)

ax.set_xlabel("Course Category")
ax.set_ylabel("Age Group")

st.pyplot(fig)

# -----------------------------
# GENDER VS LEVEL
# -----------------------------
st.subheader("Gender vs Course Level")

gender_level = pd.crosstab(
    filtered["Gender"],
    filtered["CourseLevel"]
)

fig, ax = plt.subplots(figsize=(8, 5))

gender_level.plot(
    kind="bar",
    ax=ax
)

ax.set_xlabel("Gender")
ax.set_ylabel("Enrollments")
ax.tick_params(axis="x", rotation=0)

st.pyplot(fig)

# -----------------------------
# LEARNER BEHAVIOR
# -----------------------------
st.header("📊 Learner Behavior")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Average Enrollments per Learner",
        round(learner_counts.mean(), 2)
        if len(learner_counts) > 0 else 0
    )

with col2:

    st.metric(
        "Maximum Enrollments by One Learner",
        learner_counts.max()
        if len(learner_counts) > 0 else 0
    )

st.subheader("Top Active Learners")

top_learners = learner_counts.sort_values(
    ascending=False
).head(10)

st.dataframe(top_learners)

# -----------------------------
# BEGINNER VS ADVANCED
# -----------------------------
st.subheader("Course Level Preference by Age Group")

level_age = pd.crosstab(
    filtered["AgeGroup"],
    filtered["CourseLevel"]
)

fig, ax = plt.subplots(figsize=(9, 5))

level_age.plot(
    kind="bar",
    ax=ax
)

ax.set_xlabel("Age Group")
ax.set_ylabel("Enrollments")
ax.tick_params(axis="x", rotation=0)

st.pyplot(fig)

# -----------------------------
# KEY INSIGHTS
# -----------------------------
st.header("💡 Key Insights")

st.write("""
• The 26–35 age group has the highest learner participation.

• Female learners form the largest gender group.

• Data Science is the most popular course category.

• Free courses receive the highest number of enrollments.

• Beginner-level courses are the most preferred.

• Learners take an average of 3.33 courses each.

• Some highly active learners have enrolled in up to 16 courses.

• Data Science is highly preferred among 18–25 and 26–35 learners,
while Finance is the leading category among learners below 18.
""")

# -----------------------------
# RECOMMENDATIONS
# -----------------------------
st.header("🎯 Recommendations")

st.write("""
• Expand and regularly update Data Science course offerings.

• Provide more beginner-friendly courses with clear pathways
  toward intermediate and advanced levels.

• Continue providing accessible and free introductory courses
  to encourage wider participation.

• Develop course offerings according to the preferences observed
  across different age groups.

• Maintain inclusive learning opportunities for all genders.

• Study the learning patterns of highly active learners to improve
  learner engagement.
""")

# -----------------------------
# CONCLUSION
# -----------------------------
st.header("🏁 Conclusion")

st.write("""
The analysis provides descriptive learner intelligence for EduPro.
The findings show clear differences in learner participation,
course category preferences and course-level choices across
demographic groups.

These insights can support better course planning, learner
engagement, accessibility and inclusive education strategies.
""")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")

st.caption(
    "EduPro Learner Demographics and Course Enrollment Behavior Analysis"
)
