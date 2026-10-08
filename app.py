import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE
# -----------------------------
st.set_page_config(
    page_title="EduPro Learner Analytics",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 EduPro Learner Demographics & Course Enrollment Analysis")
st.write("Interactive analysis of learner demographics and course enrollment behavior.")

# -----------------------------
# LOAD DATA
# -----------------------------
file_path = "EduPro Online Platform.xlsx"

users = pd.read_excel(file_path, sheet_name="Users")
courses = pd.read_excel(file_path, sheet_name="Courses")
transactions = pd.read_excel(file_path, sheet_name="Transactions")

# -----------------------------
# MERGE DATA
# -----------------------------
data = pd.merge(users, transactions, on="UserID")
data = pd.merge(data, courses, on="CourseID")

# -----------------------------
# AGE GROUP
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
# SIDEBAR FILTERS
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
# FILTER DATA
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
st.header("📌 Key Metrics")

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
    round(learner_counts.mean(), 2)
    if len(learner_counts) > 0 else 0
)

col4.metric(
    "Popular Category",
    filtered["CourseCategory"].value_counts().idxmax()
    if len(filtered) > 0 else "N/A"
)

# -----------------------------
# DEMOGRAPHICS
# -----------------------------
st.header("👥 Learner Demographics")

col1, col2 = st.columns(2)

with col1:

    age_counts = (
        filtered["AgeGroup"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    age_counts.columns = ["AgeGroup", "Enrollments"]

    fig = px.bar(
        age_counts,
        x="AgeGroup",
        y="Enrollments",
        title="Learners by Age Group",
        text="Enrollments"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    gender_counts = (
        filtered["Gender"]
        .value_counts()
        .reset_index()
    )

    gender_counts.columns = ["Gender", "Enrollments"]

    fig = px.bar(
        gender_counts,
        x="Gender",
        y="Enrollments",
        title="Gender Participation",
        text="Enrollments"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# AGE-WISE ENROLLMENT
# -----------------------------
st.header("📈 Age-wise Enrollment")

age_enrollment = (
    filtered["AgeGroup"]
    .value_counts()
    .sort_index()
    .reset_index()
)

age_enrollment.columns = ["AgeGroup", "Enrollments"]

fig = px.bar(
    age_enrollment,
    x="AgeGroup",
    y="Enrollments",
    title="Enrollments Across Age Groups",
    text="Enrollments"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# COURSE CATEGORY
# -----------------------------
st.header("📚 Course Preferences")

category_counts = (
    filtered["CourseCategory"]
    .value_counts()
    .reset_index()
)

category_counts.columns = ["CourseCategory", "Enrollments"]

fig = px.bar(
    category_counts,
    x="CourseCategory",
    y="Enrollments",
    title="Course Category Popularity",
    text="Enrollments"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# COURSE LEVEL
# -----------------------------
level_counts = (
    filtered["CourseLevel"]
    .value_counts()
    .reset_index()
)

level_counts.columns = ["CourseLevel", "Enrollments"]

fig = px.bar(
    level_counts,
    x="CourseLevel",
    y="Enrollments",
    title="Course Level Preference",
    text="Enrollments"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# COURSE TYPE
# -----------------------------
type_counts = (
    filtered["CourseType"]
    .value_counts()
    .reset_index()
)

type_counts.columns = ["CourseType", "Enrollments"]

fig = px.bar(
    type_counts,
    x="CourseType",
    y="Enrollments",
    title="Course Type Popularity",
    text="Enrollments"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# AGE GROUP VS CATEGORY
# -----------------------------
st.header("🔥 Demographic Course Preferences")

age_category = pd.crosstab(
    filtered["AgeGroup"],
    filtered["CourseCategory"]
)

fig = px.imshow(
    age_category,
    text_auto=True,
    aspect="auto",
    title="Age Group vs Course Category"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# GENDER VS LEVEL
# -----------------------------
gender_level = pd.crosstab(
    filtered["Gender"],
    filtered["CourseLevel"]
)

gender_level = gender_level.reset_index()

fig = px.bar(
    gender_level,
    x="Gender",
    y=gender_level.columns[1:].tolist(),
    barmode="group",
    title="Gender vs Course Level"
)

st.plotly_chart(fig, use_container_width=True)

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

# -----------------------------
# TOP ACTIVE LEARNERS
# -----------------------------
st.subheader("Top 10 Active Learners")

top_learners = (
    learner_counts
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

top_learners.columns = ["UserID", "Enrollments"]

fig = px.bar(
    top_learners,
    x="UserID",
    y="Enrollments",
    title="Top 10 Active Learners",
    text="Enrollments"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# LEVEL BY AGE GROUP
# -----------------------------
st.subheader("Course Level Preference by Age Group")

level_age = pd.crosstab(
    filtered["AgeGroup"],
    filtered["CourseLevel"]
)

level_age = level_age.reset_index()

fig = px.bar(
    level_age,
    x="AgeGroup",
    y=level_age.columns[1:].tolist(),
    barmode="group",
    title="Course Level Preference by Age Group"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# KEY INSIGHTS
# -----------------------------
st.header("💡 Key Insights")

st.markdown("""
- **26–35** is the most active age group.
- **Female learners** form the largest gender group.
- **Data Science** is the most popular course category.
- **Free courses** have the highest enrollments.
- **Beginner-level courses** are the most preferred.
- Learners take an average of **3.33 courses** each.
- The maximum enrollment by one learner is **16 courses**.
- Data Science is highly preferred among **18–25 and 26–35** learners.
- Finance is the leading category among learners **below 18**.
- Both male and female learners show the highest preference for **Beginner courses**.
""")

# -----------------------------
# RECOMMENDATIONS
# -----------------------------
st.header("🎯 Recommendations")

st.markdown("""
1. **Expand Data Science offerings**  
   Continue developing and updating Data Science courses based on its strong learner demand.

2. **Strengthen beginner learning paths**  
   Provide more beginner-friendly courses and clear pathways toward intermediate and advanced levels.

3. **Maintain accessible learning options**  
   Continue offering free introductory courses to encourage wider learner participation.

4. **Consider age-based preferences**  
   Develop course offerings according to the different preferences observed across age groups.

5. **Promote inclusive learning**  
   Maintain accessible learning opportunities across different gender groups.

6. **Support active learners**  
   Study the learning patterns of highly active learners to improve learner engagement.
""")

# -----------------------------
# CONCLUSION
# -----------------------------
st.header("🏁 Conclusion")

st.write("""
The analysis provides descriptive learner intelligence for EduPro.
The findings reveal clear patterns in learner demographics,
course preferences and enrollment behavior.

These insights can support better course planning, learner
engagement, accessibility and inclusive education strategies.
""")

st.markdown("---")

st.caption(
    "EduPro Learner Demographics and Course Enrollment Behavior Analysis"
)
