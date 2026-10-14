import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EduPro Learner Analytics", page_icon="🎓", layout="wide")
st.title("🎓 EduPro – Learner Analysis and Course Insights")
st.caption("Explore learner demographics, course preferences, and enrollment patterns.")

@st.cache_data
def load_data():
    file_path = "EduPro Online Platform.xlsx"
    users = pd.read_excel(file_path, sheet_name="Users")
    courses = pd.read_excel(file_path, sheet_name="Courses")
    transactions = pd.read_excel(file_path, sheet_name="Transactions")
    data = users.merge(transactions, on="UserID", how="inner").merge(courses, on="CourseID", how="inner")

    def make_age_group(age):
        if pd.isna(age):
            return "Unknown"
        if age < 18:
            return "<18"
        if age <= 25:
            return "18-25"
        if age <= 35:
            return "26-35"
        if age <= 45:
            return "36-45"
        return "45+"

    data["AgeGroup"] = data["Age"].apply(make_age_group)
    return data

try:
    data = load_data()
except FileNotFoundError:
    st.error("Could not find 'EduPro Online Platform.xlsx'. Keep it in the same folder as app.py.")
    st.stop()
except Exception as exc:
    st.error(f"Could not load the workbook: {exc}")
    st.stop()

age_order = ["<18", "18-25", "26-35", "36-45", "45+", "Unknown"]
data["AgeGroup"] = pd.Categorical(data["AgeGroup"], categories=age_order, ordered=True)

st.sidebar.header("🔎 Filters")
age_options = [x for x in age_order if x in data["AgeGroup"].astype(str).unique()]
gender_options = sorted(data["Gender"].dropna().unique().tolist())
category_options = sorted(data["CourseCategory"].dropna().unique().tolist())
level_options = sorted(data["CourseLevel"].dropna().unique().tolist())

age_filter = st.sidebar.multiselect("Age Group", age_options, default=age_options)
gender_filter = st.sidebar.multiselect("Gender", gender_options, default=gender_options)
category_filter = st.sidebar.multiselect("Course Category", category_options, default=category_options)
level_filter = st.sidebar.multiselect("Course Level", level_options, default=level_options)

if not all([age_filter, gender_filter, category_filter, level_filter]):
    st.warning("Select at least one option in every filter.")
    st.stop()

filtered = data[
    data["AgeGroup"].astype(str).isin(age_filter)
    & data["Gender"].isin(gender_filter)
    & data["CourseCategory"].isin(category_filter)
    & data["CourseLevel"].isin(level_filter)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Select more options.")
    st.stop()

st.header("📌 Key Metrics")
unique_learners = filtered["UserID"].nunique()
total_enrollments = len(filtered)
course_counts = filtered.groupby("UserID")["CourseID"].nunique()
average_courses = round(course_counts.mean(), 2) if not course_counts.empty else 0
popular_category = filtered["CourseCategory"].value_counts().idxmax()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Enrollments", f"{total_enrollments:,}")
c2.metric("Unique Learners", f"{unique_learners:,}")
c3.metric("Avg. Courses per Learner", f"{average_courses:.2f}")
c4.metric("Most Popular Category", popular_category)
st.caption("All metrics and charts respond to the selected filters. One learner can have multiple enrollments.")

st.header("👥 Learner Demographics")
c1, c2 = st.columns(2)

with c1:
    by_age = filtered.groupby("AgeGroup", observed=False)["UserID"].nunique()
    by_age = by_age.reindex([x for x in age_order if x in age_filter], fill_value=0)
    age_people = by_age.rename_axis("Age Group").reset_index(name="Unique Learners")
    fig = px.bar(age_people, x="Age Group", y="Unique Learners", text="Unique Learners",
                 title="Unique Learners by Age Group")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    by_gender = filtered.groupby("Gender")["UserID"].nunique().sort_values(ascending=False)
    gender_people = by_gender.rename_axis("Gender").reset_index(name="Unique Learners")
    fig = px.bar(gender_people, x="Gender", y="Unique Learners", text="Unique Learners",
                 title="Unique Learners by Gender")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

st.header("📈 Enrollment Activity")
age_enrollment = filtered.groupby("AgeGroup", observed=False).size().reindex(
    [x for x in age_order if x in age_filter], fill_value=0
).rename_axis("Age Group").reset_index(name="Enrollments")
fig = px.bar(age_enrollment, x="Age Group", y="Enrollments", text="Enrollments",
             title="Enrollments Across Age Groups")
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)

st.header("📚 Course Preferences")
c1, c2 = st.columns(2)
with c1:
    category_counts = filtered["CourseCategory"].value_counts().rename_axis("Course Category").reset_index(name="Enrollments")
    category_counts = category_counts.sort_values("Enrollments", ascending=True)
    fig = px.bar(category_counts, x="Enrollments", y="Course Category", orientation="h",
                 text="Enrollments", title="Course Category Popularity")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    level_counts = filtered["CourseLevel"].value_counts().rename_axis("Course Level").reset_index(name="Enrollments")
    level_counts = level_counts.sort_values("Enrollments", ascending=True)
    fig = px.bar(level_counts, x="Enrollments", y="Course Level", orientation="h",
                 text="Enrollments", title="Course Level Preference")
    st.plotly_chart(fig, use_container_width=True)

st.header("🔍 Demographic Course Preferences")
c1, c2 = st.columns(2)
with c1:
    age_category = pd.crosstab(filtered["AgeGroup"].astype(str), filtered["CourseCategory"])
    age_category = age_category.reindex([x for x in age_order if x in age_filter], fill_value=0)
    fig = px.imshow(age_category, text_auto=True, aspect="auto", title="Age Group vs Course Category",
                    labels={"x": "Course Category", "y": "Age Group", "color": "Enrollments"})
    st.plotly_chart(fig, use_container_width=True)
with c2:
    gender_level = pd.crosstab(filtered["Gender"], filtered["CourseLevel"]).reset_index()
    levels = [col for col in gender_level.columns if col != "Gender"]
    fig = px.bar(gender_level, x="Gender", y=levels, barmode="group", title="Gender vs Course Level",
                 labels={"value": "Enrollments", "variable": "Course Level"})
    st.plotly_chart(fig, use_container_width=True)

st.header("💡 Key Insights")
top_age = age_enrollment.loc[age_enrollment["Enrollments"].idxmax(), "Age Group"]
top_category = category_counts.sort_values("Enrollments", ascending=False).iloc[0]["Course Category"]
top_level = level_counts.sort_values("Enrollments", ascending=False).iloc[0]["Course Level"]
st.markdown(
    f"- **Most enrollments by age group:** {top_age}\n"
    f"- **Most popular category in the selected data:** {top_category}\n"
    f"- **Most popular course level in the selected data:** {top_level}\n"
    f"- **Unique learners in the selected data:** {unique_learners:,}\n\n"
    "These are descriptive patterns; they do not prove causes or predict future behavior."
)
st.header("🏁 Conclusion")
st.write("EduPro combines learner, course, and enrollment data to explore demographics and course preferences. "
         "The dashboard clearly separates unique learners from enrollment records and supports interactive filtering.")
st.markdown("---")
st.caption("EduPro – Learner Analysis and Course Insights")
