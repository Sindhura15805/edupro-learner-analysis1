import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EduPro Learner Analytics", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; max-width: 1450px;}
.hero {padding: 1.25rem 1.5rem; border-radius: 15px; color: white;
background: linear-gradient(110deg,#14213d,#176b78); margin-bottom: 1rem;}
.hero h1 {color:white; margin:0;}
.hero p {color:#e2edf5; margin:.35rem 0 0;}
div[data-testid="stMetric"] {background:rgba(120,130,150,.08); padding:12px; border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🎓 EduPro — Learner Analysis and Course Insights</h1>
<p>Descriptive analysis of learner demographics, course preferences and enrollment behaviour.</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    users = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Users")
    courses = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Courses")
    transactions = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Transactions")
    df = transactions.merge(users, on="UserID", how="left").merge(courses, on="CourseID", how="left")
    def age_group(age):
        if pd.isna(age): return "Unknown"
        if age < 18: return "<18"
        if age <= 25: return "18-25"
        if age <= 35: return "26-35"
        if age <= 45: return "36-45"
        return "45+"
    df["AgeGroup"] = df["Age"].apply(age_group)
    if "TransactionDate" in df.columns:
        df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], errors="coerce")
    return df

try:
    data = load_data()
except Exception as e:
    st.error(f"Could not load workbook. Ensure 'EduPro Online Platform.xlsx' is beside this app.py. Details: {e}")
    st.stop()

age_order = ["<18", "18-25", "26-35", "36-45", "45+", "Unknown"]
ages = [x for x in age_order if x in data["AgeGroup"].unique()]
st.sidebar.header("🔎 Filters")
age_f = st.sidebar.multiselect("Age Group", ages, default=ages)
gender_f = st.sidebar.multiselect("Gender", sorted(data["Gender"].dropna().unique()), default=sorted(data["Gender"].dropna().unique()))
cat_f = st.sidebar.multiselect("Course Category", sorted(data["CourseCategory"].dropna().unique()), default=sorted(data["CourseCategory"].dropna().unique()))
level_f = st.sidebar.multiselect("Course Level", sorted(data["CourseLevel"].dropna().unique()), default=sorted(data["CourseLevel"].dropna().unique()))
type_f = st.sidebar.multiselect("Course Type", sorted(data["CourseType"].dropna().unique()), default=sorted(data["CourseType"].dropna().unique()))
if not all([age_f, gender_f, cat_f, level_f, type_f]):
    st.warning("Select at least one value in every filter.")
    st.stop()

df = data[data["AgeGroup"].isin(age_f) & data["Gender"].isin(gender_f) &
          data["CourseCategory"].isin(cat_f) & data["CourseLevel"].isin(level_f) &
          data["CourseType"].isin(type_f)].copy()
if df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# Metrics
enrollments = len(df)
learners = df["UserID"].nunique()
unique_courses_per_learner = df.groupby("UserID")["CourseID"].nunique()
avg_courses = unique_courses_per_learner.mean() if len(unique_courses_per_learner) else 0
popular_category = df["CourseCategory"].value_counts().idxmax()
k1,k2,k3,k4 = st.columns(4)
k1.metric("Total Enrollments", f"{enrollments:,}")
k2.metric("Unique Learners", f"{learners:,}")
k3.metric("Avg. Unique Courses / Learner", f"{avg_courses:.2f}")
k4.metric("Most Popular Category", str(popular_category))
st.caption("Learners are unique people. Enrollments are course-registration records; one learner can have several enrollments.")

# Main analysis: focus on learner demographics, course preferences, and enrollment behaviour.

# Original charts, with the age chart corrected to count unique people
st.header("👥 Learner Demographics")
c1,c2 = st.columns(2)
with c1:
    d = df.groupby("AgeGroup")["UserID"].nunique().reindex([a for a in age_order if a in age_f], fill_value=0).rename_axis("Age Group").reset_index(name="Unique Learners")
    fig = px.bar(d, x="Age Group", y="Unique Learners", text="Unique Learners", title="Learners by Age Group")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    d = df.groupby("Gender")["UserID"].nunique().rename_axis("Gender").reset_index(name="Unique Learners")
    fig = px.bar(d, x="Gender", y="Unique Learners", text="Unique Learners", title="Gender Participation")
    st.plotly_chart(fig, use_container_width=True)

st.header("📈 Age-wise Enrollment")
d = df.groupby("AgeGroup").size().reindex([a for a in age_order if a in age_f], fill_value=0).rename_axis("Age Group").reset_index(name="Enrollments")
fig = px.bar(d, x="Age Group", y="Enrollments", text="Enrollments", title="Enrollments Across Age Groups")
st.plotly_chart(fig, use_container_width=True)

st.header("📚 Course Preferences")
c1,c2 = st.columns(2)
with c1:
    d = df["CourseCategory"].value_counts().rename_axis("Course Category").reset_index(name="Enrollments")
    fig = px.bar(d, x="Enrollments", y="Course Category", orientation="h", title="Course Category Popularity")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    d = df["CourseLevel"].value_counts().rename_axis("Course Level").reset_index(name="Enrollments")
    fig = px.bar(d, x="Enrollments", y="Course Level", orientation="h", title="Course Level Preference")
    st.plotly_chart(fig, use_container_width=True)
c1,c2 = st.columns(2)
with c1:
    d = df["CourseType"].value_counts().rename_axis("Course Type").reset_index(name="Enrollments")
    fig = px.pie(d, names="Course Type", values="Enrollments", hole=.45, title="Course Type Popularity — Free vs Paid")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    d = df.groupby("CourseName").size().sort_values(ascending=False).head(10).sort_values().rename_axis("Course").reset_index(name="Enrollments")
    fig = px.bar(d, x="Enrollments", y="Course", orientation="h", title="Top 10 Courses by Enrollment")
    st.plotly_chart(fig, use_container_width=True)

st.header("🔥 Demographic Course Preferences")
c1,c2 = st.columns(2)
with c1:
    d = pd.crosstab(df["AgeGroup"], df["CourseCategory"]).reindex([a for a in age_order if a in age_f], fill_value=0)
    fig = px.imshow(d, text_auto=True, aspect="auto", title="Age Group vs Course Category",
                    labels={"x":"Course Category","y":"Age Group","color":"Enrollments"})
    st.plotly_chart(fig, use_container_width=True)
with c2:
    d = pd.crosstab(df["Gender"], df["CourseLevel"]).reset_index()
    levels = [x for x in d.columns if x != "Gender"]
    fig = px.bar(d, x="Gender", y=levels, barmode="group", title="Gender vs Course Level")
    st.plotly_chart(fig, use_container_width=True)

st.header("📊 Learner Behavior")
counts = df.groupby("UserID").size()
unique_counts = df.groupby("UserID")["CourseID"].nunique()
a,b,c = st.columns(3)
a.metric("Average Enrollments / Learner", f"{counts.mean():.2f}" if len(counts) else "0")
b.metric("Maximum Enrollments by One Learner", f"{int(counts.max())}" if len(counts) else "0")
c.metric("Learners with 2+ Unique Courses", f"{int((unique_counts > 1).sum()):,}")
d = counts.sort_values(ascending=False).head(10).rename_axis("UserID").reset_index(name="Enrollments")
fig = px.bar(d, x="UserID", y="Enrollments", title="Top 10 Active Learners", text="Enrollments")
st.plotly_chart(fig, use_container_width=True)
d = pd.crosstab(df["AgeGroup"], df["CourseLevel"]).reindex([a for a in age_order if a in age_f], fill_value=0).reset_index()
levels = [x for x in d.columns if x != "AgeGroup"]
fig = px.bar(d, x="AgeGroup", y=levels, barmode="group", title="Course Level Preference by Age Group")
st.plotly_chart(fig, use_container_width=True)

# Only two extra sections: useful and explainable
st.header("🆕 Additional Analysis")
if "TransactionDate" in df.columns and df["TransactionDate"].notna().any():
    monthly_df = df.dropna(subset=["TransactionDate"]).copy()
    monthly_df["Month"] = monthly_df["TransactionDate"].dt.to_period("M").dt.to_timestamp()
    monthly = monthly_df.groupby("Month").size().rename("Enrollments").reset_index()
    fig = px.line(monthly, x="Month", y="Enrollments", markers=True, title="Monthly Enrollment Trend")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Monthly trend is unavailable because the filtered records do not contain valid transaction dates.")

freq = counts.value_counts().sort_index().rename_axis("Enrollments per Learner").reset_index(name="Number of Learners")
fig = px.bar(freq, x="Enrollments per Learner", y="Number of Learners", title="Learner Enrollment Frequency")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Course Enrollment Detail")
summary = df.groupby(["CourseName","CourseCategory","CourseLevel","CourseType"]).size().rename("Enrollments").reset_index().sort_values("Enrollments", ascending=False)
st.dataframe(summary, use_container_width=True, hide_index=True)
st.download_button("Download course summary as CSV", summary.to_csv(index=False).encode("utf-8"),
                   file_name="edupro_course_summary.csv", mime="text/csv")

# Supporting checks: data quality for an education/enrollment dataset
st.header("🧹 Data Quality Checks")
st.write("These checks help assess whether learner, course and enrollment records are complete and consistent before interpreting the dashboard. They flag potential issues; they do not automatically delete or change records.")

with st.expander("View data quality results", expanded=False):
    try:
        users_raw = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Users")
        courses_raw = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Courses")
        transactions_raw = pd.read_excel("EduPro Online Platform.xlsx", sheet_name="Transactions")

        # Check the source sheets separately so repeated joins do not inflate counts.
        user_missing = int(users_raw.isna().sum().sum())
        course_missing = int(courses_raw.isna().sum().sum())
        transaction_missing = int(transactions_raw.isna().sum().sum())
        exact_dupes = int(transactions_raw.duplicated().sum())
        missing_user_ids = int(transactions_raw["UserID"].isna().sum()) if "UserID" in transactions_raw else 0
        missing_course_ids = int(transactions_raw["CourseID"].isna().sum()) if "CourseID" in transactions_raw else 0
        unknown_users = int((~transactions_raw["UserID"].isin(users_raw["UserID"]) & transactions_raw["UserID"].notna()).sum()) if {"UserID"}.issubset(transactions_raw.columns) and "UserID" in users_raw else 0
        unknown_courses = int((~transactions_raw["CourseID"].isin(courses_raw["CourseID"]) & transactions_raw["CourseID"].notna()).sum()) if "CourseID" in transactions_raw and "CourseID" in courses_raw else 0

        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Missing values — Users", f"{user_missing:,}")
        q2.metric("Missing values — Courses", f"{course_missing:,}")
        q3.metric("Missing values — Transactions", f"{transaction_missing:,}")
        q4.metric("Exact duplicate transaction rows", f"{exact_dupes:,}")

        integrity = pd.DataFrame({
            "Check": ["Enrollment missing UserID", "Enrollment missing CourseID", "UserID not found in Users sheet", "CourseID not found in Courses sheet"],
            "Records flagged": [missing_user_ids, missing_course_ids, unknown_users, unknown_courses]
        })
        st.subheader("Enrollment consistency")
        st.dataframe(integrity, use_container_width=True, hide_index=True)

        if "Age" in users_raw.columns:
            ages_numeric = pd.to_numeric(users_raw["Age"], errors="coerce")
            invalid_age = int(((ages_numeric < 0) | (ages_numeric > 100)).sum())
            st.metric("Age values outside 0–100", f"{invalid_age:,}")
        if {"UserID", "CourseID"}.issubset(transactions_raw.columns):
            repeated_pairs = int(transactions_raw.duplicated(subset=["UserID", "CourseID"], keep=False).sum())
            st.metric("Rows in repeated learner-course pairs", f"{repeated_pairs:,}")
            st.caption("Repeated learner-course pairs are flagged for review, not automatically treated as errors: a learner may legitimately enrol in the same course more than once.")
        st.caption("A non-zero count is a prompt to investigate the source data. It does not by itself prove that a record is wrong.")
    except Exception as e:
        st.warning(f"Data quality checks could not be completed: {e}")

st.header("💡 Key Insights")
age_top = df["AgeGroup"].value_counts().idxmax()
cat_top = df["CourseCategory"].value_counts().idxmax()
level_top = df["CourseLevel"].value_counts().idxmax()
type_top = df["CourseType"].value_counts().idxmax()
st.markdown(f"""
- **Highest enrollment age group:** {age_top}
- **Most popular course category:** {cat_top}
- **Most popular course level:** {level_top}
- **Most enrolled course type:** {type_top}
- **Unique learners in current filter:** {learners:,}
""")
st.header("🎯 Recommendations")
st.markdown(f"""
1. Review course availability and content for **{cat_top}**, the leading category in the selected data.
2. Make learning pathways clear around **{level_top}** courses and routes to other levels.
3. Compare **{type_top}** enrollments with revenue and completion data before making pricing decisions.
4. Use age/category patterns to investigate learner interests, without assuming age causes preferences.
5. Track enrollment trends over time where valid dates are available.
""")
st.info("EduPro is a descriptive analytics project. These charts identify patterns; they do not predict outcomes or prove causes.")
st.header("🏁 Conclusion")
st.write("EduPro combines learner, course and transaction data to understand demographics, course preferences and enrollment behaviour. It presents descriptive insights through interactive charts and filters.")
st.caption("EduPro — Learner Analysis and Course Insights | Python · Pandas · Plotly Express · Streamlit")
