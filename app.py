import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page
st.title("EduPro Learner Demographics and Course Enrollment Analysis")

# Load data
file_path = "EduPro Online Platform.xlsx"

users = pd.read_excel(file_path, sheet_name="Users")
courses = pd.read_excel(file_path, sheet_name="Courses")
transactions = pd.read_excel(file_path, sheet_name="Transactions")

# Merge data
data = pd.merge(users, transactions, on="UserID")
data = pd.merge(data, courses, on="CourseID")

# Create age groups
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

# Sidebar filters
st.sidebar.header("Filters")

age = st.sidebar.multiselect(
    "Age Group",
    data["AgeGroup"].unique(),
    default=data["AgeGroup"].unique()
)

gender = st.sidebar.multiselect(
    "Gender",
    data["Gender"].unique(),
    default=data["Gender"].unique()
)

category = st.sidebar.multiselect(
    "Course Category",
    data["CourseCategory"].unique(),
    default=data["CourseCategory"].unique()
)

level = st.sidebar.multiselect(
    "Course Level",
    data["CourseLevel"].unique(),
    default=data["CourseLevel"].unique()
)

# Apply filters
filtered = data[
    data["AgeGroup"].isin(age) &
    data["Gender"].isin(gender) &
    data["CourseCategory"].isin(category) &
    data["CourseLevel"].isin(level)
]

# KPIs
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Enrollments", len(filtered))
col2.metric("Learners", filtered["UserID"].nunique())

if len(filtered) > 0:
    col3.metric(
        "Popular Category",
        filtered["CourseCategory"].value_counts().idxmax()
    )
    col4.metric(
        "Popular Level",
        filtered["CourseLevel"].value_counts().idxmax()
    )

# Age-wise enrollment
st.subheader("Enrollments by Age Group")

age_counts = filtered["AgeGroup"].value_counts().sort_index()

fig, ax = plt.subplots()
sns.barplot(x=age_counts.index, y=age_counts.values, ax=ax)
ax.set_xlabel("Age Group")
ax.set_ylabel("Enrollments")
st.pyplot(fig)

# Gender analysis
st.subheader("Gender Participation")

gender_counts = filtered["Gender"].value_counts()

fig, ax = plt.subplots()
sns.barplot(x=gender_counts.index, y=gender_counts.values, ax=ax)
ax.set_xlabel("Gender")
ax.set_ylabel("Enrollments")
st.pyplot(fig)

# Course category
st.subheader("Course Category Popularity")

category_counts = filtered["CourseCategory"].value_counts()

fig, ax = plt.subplots()
sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax)
ax.set_xlabel("Course Category")
ax.set_ylabel("Enrollments")
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)

# Course level
st.subheader("Course Level Preference")

level_counts = filtered["CourseLevel"].value_counts()

fig, ax = plt.subplots()
sns.barplot(x=level_counts.index, y=level_counts.values, ax=ax)
ax.set_xlabel("Course Level")
ax.set_ylabel("Enrollments")
st.pyplot(fig)

# Age group vs category
st.subheader("Age Group vs Course Category")

age_category = pd.crosstab(
    filtered["AgeGroup"],
    filtered["CourseCategory"]
)

fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(age_category, annot=True, fmt="d", ax=ax)
ax.set_xlabel("Course Category")
ax.set_ylabel("Age Group")
st.pyplot(fig)

# Gender vs course level
st.subheader("Gender vs Course Level")

gender_level = pd.crosstab(
    filtered["Gender"],
    filtered["CourseLevel"]
)

fig, ax = plt.subplots()
gender_level.plot(kind="bar", ax=ax)
ax.set_xlabel("Gender")
ax.set_ylabel("Enrollments")
ax.tick_params(axis="x", rotation=0)
st.pyplot(fig)
