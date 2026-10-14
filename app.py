import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# EduPro | Premium Learner & Course Intelligence Dashboard
# ---------------------------------------------------------
st.set_page_config(
    page_title="EduPro | Learner Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling without external assets
st.markdown("""
<style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2.5rem; max-width: 1500px;}
    [data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.22);}
    .hero {
        padding: 1.35rem 1.55rem; border-radius: 18px; margin-bottom: 1rem;
        background: linear-gradient(120deg, #101c3a 0%, #183e67 55%, #166a78 100%);
        color: white;
    }
    .hero h1 {color: white; margin: 0; font-size: 2rem;}
    .hero p {color: #dce9f7; margin: .35rem 0 0 0; font-size: 1rem;}
    .section-note {color: #6b7280; font-size: .92rem; margin-top: -.5rem;}
    div[data-testid="stMetric"] {
        background: rgba(128,128,128,.07); border: 1px solid rgba(128,128,128,.18);
        padding: 15px 16px; border-radius: 14px;
    }
    .insight {
        border: 1px solid rgba(128,128,128,.22); border-left: 4px solid #20a4a8;
        padding: 12px 15px; border-radius: 10px; margin: 8px 0;
        background: rgba(128,128,128,.045);
    }
    .small-muted {color: #6b7280; font-size: .85rem;}
    div[data-testid="stTabs"] button {font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# Plotly template
PLOT_LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=18, r=18, t=60, b=18),
    font=dict(family="Arial", size=12, color="#263247"),
    legend_title_text=""
)

@st.cache_data
def load_data():
    workbook = "EduPro Online Platform.xlsx"
    users = pd.read_excel(workbook, sheet_name="Users")
    courses = pd.read_excel(workbook, sheet_name="Courses")
    transactions = pd.read_excel(workbook, sheet_name="Transactions")

    # Keep transaction rows as the unit of enrollment analysis
    data = transactions.merge(users, on="UserID", how="left")
    data = data.merge(courses, on="CourseID", how="left")

    def age_group(age):
        if pd.isna(age):
            return "Unknown"
        if age < 18:
            return "<18"
        if age <= 25:
            return "18–25"
        if age <= 35:
            return "26–35"
        if age <= 45:
            return "36–45"
        return "45+"

    data["AgeGroup"] = data["Age"].apply(age_group)
    if "TransactionDate" in data.columns:
        data["TransactionDate"] = pd.to_datetime(data["TransactionDate"], errors="coerce")
    return data

try:
    data = load_data()
except FileNotFoundError:
    st.error("Workbook not found. Keep **EduPro Online Platform.xlsx** in the same folder as this app.")
    st.stop()
except Exception as exc:
    st.error(f"Unable to load the workbook. Check sheet and column names. Details: {exc}")
    st.stop()

age_order = ["<18", "18–25", "26–35", "36–45", "45+", "Unknown"]
available_ages = [a for a in age_order if a in data["AgeGroup"].astype(str).unique()]
gender_options = sorted(data["Gender"].dropna().unique().tolist())
category_options = sorted(data["CourseCategory"].dropna().unique().tolist())
level_options = sorted(data["CourseLevel"].dropna().unique().tolist())
type_options = sorted(data["CourseType"].dropna().unique().tolist())

# Sidebar
st.sidebar.markdown("## 🎓 EduPro")
st.sidebar.caption("LEARNER INTELLIGENCE")
st.sidebar.markdown("---")
st.sidebar.markdown("### Refine your analysis")

age_filter = st.sidebar.multiselect("Age group", available_ages, default=available_ages)
gender_filter = st.sidebar.multiselect("Gender", gender_options, default=gender_options)
category_filter = st.sidebar.multiselect("Course category", category_options, default=category_options)
level_filter = st.sidebar.multiselect("Course level", level_options, default=level_options)
type_filter = st.sidebar.multiselect("Course type", type_options, default=type_options)

if st.sidebar.button("Reset all filters", use_container_width=True):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Filters apply to the overview and all analytical charts.")

if not all([age_filter, gender_filter, category_filter, level_filter, type_filter]):
    st.warning("Choose at least one value in every filter to display results.")
    st.stop()

filtered = data[
    data["AgeGroup"].astype(str).isin(age_filter)
    & data["Gender"].isin(gender_filter)
    & data["CourseCategory"].isin(category_filter)
    & data["CourseLevel"].isin(level_filter)
    & data["CourseType"].isin(type_filter)
].copy()

if filtered.empty:
    st.warning("No records match the current filters. Expand one or more filter selections.")
    st.stop()

# Derived metrics
n_enrollments = len(filtered)
n_learners = filtered["UserID"].nunique()
courses_per_learner = filtered.groupby("UserID")["CourseID"].nunique()
avg_courses = courses_per_learner.mean() if not courses_per_learner.empty else 0
top_category = filtered["CourseCategory"].value_counts().idxmax()
top_level = filtered["CourseLevel"].value_counts().idxmax()
top_type = filtered["CourseType"].value_counts().idxmax()
repeat_learners = int((courses_per_learner > 1).sum())
repeat_rate = (repeat_learners / n_learners * 100) if n_learners else 0
enrollments_per_learner = filtered.groupby("UserID").size()

# Hero
st.markdown("""
<div class="hero">
  <h1>EduPro Learner Intelligence</h1>
  <p>Understand who learns, what they choose, and how enrollment activity changes across learner groups.</p>
</div>
""", unsafe_allow_html=True)

# Overview metrics
st.markdown("### Executive overview")
st.markdown('<p class="section-note">A live snapshot based on your current filter selections.</p>', unsafe_allow_html=True)
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total enrollments", f"{n_enrollments:,}")
m2.metric("Unique learners", f"{n_learners:,}")
m3.metric("Avg. unique courses / learner", f"{avg_courses:.2f}")
m4.metric("Repeat learners", f"{repeat_learners:,}", f"{repeat_rate:.1f}% of learners")
m5.metric("Most selected category", str(top_category))

st.markdown("---")

# Tabs make the dashboard easier to navigate
overview_tab, demographic_tab, course_tab, engagement_tab, insights_tab = st.tabs([
    "📍 Overview", "👥 Demographics", "📚 Course insights", "🔁 Engagement", "💡 Findings & actions"
])

with overview_tab:
    st.subheader("Enrollment overview")
    left, right = st.columns([1.35, 1])
    with left:
        age_enroll = filtered.groupby("AgeGroup", observed=False).size().reindex(
            [a for a in age_order if a in age_filter], fill_value=0
        ).rename_axis("Age group").reset_index(name="Enrollments")
        fig = px.bar(
            age_enroll, x="Age group", y="Enrollments", text="Enrollments",
            color="Enrollments", color_continuous_scale="Teal",
            title="Enrollment activity by age group"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, xaxis_title="", yaxis_title="Enrollments")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        category_mix = filtered["CourseCategory"].value_counts().rename_axis("Category").reset_index(name="Enrollments")
        fig = px.pie(
            category_mix, names="Category", values="Enrollments",
            hole=.62, title="Enrollment mix by category"
        )
        fig.update_traces(textposition="inside", textinfo="percent")
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    if "TransactionDate" in filtered.columns and filtered["TransactionDate"].notna().any():
        st.subheader("Enrollment trend over time")
        trend = filtered.dropna(subset=["TransactionDate"]).copy()
        trend["Month"] = trend["TransactionDate"].dt.to_period("M").dt.to_timestamp()
        trend = trend.groupby("Month").size().reset_index(name="Enrollments")
        if not trend.empty:
            fig = px.line(trend, x="Month", y="Enrollments", markers=True, title="Monthly enrollments")
            fig.update_traces(line_width=3)
            fig.update_layout(**PLOT_LAYOUT, xaxis_title="Month", yaxis_title="Enrollments")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("A monthly trend will appear when valid TransactionDate values are available.")

with demographic_tab:
    st.subheader("Who is learning?")
    a, b = st.columns(2)
    with a:
        people_age = filtered.groupby("AgeGroup", observed=False)["UserID"].nunique().reindex(
            [x for x in age_order if x in age_filter], fill_value=0
        ).rename_axis("Age group").reset_index(name="Unique learners")
        fig = px.bar(people_age, x="Age group", y="Unique learners", text="Unique learners",
                     title="Unique learners by age group", color="Unique learners",
                     color_continuous_scale="Blues")
        fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, xaxis_title="", yaxis_title="Unique learners")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    with b:
        people_gender = filtered.groupby("Gender")["UserID"].nunique().rename_axis("Gender").reset_index(name="Unique learners")
        fig = px.pie(people_gender, names="Gender", values="Unique learners", hole=.55,
                     title="Learner composition by gender")
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    age_gender = pd.crosstab(filtered["AgeGroup"].astype(str), filtered["Gender"])
    st.subheader("Age group × gender")
    fig = px.imshow(age_gender, text_auto=True, aspect="auto", title="Learner/enrollment records by age group and gender",
                    labels={"x": "Gender", "y": "Age group", "color": "Records"})
    fig.update_layout(**PLOT_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("The heatmap counts rows in the filtered enrollment-level dataset. Use the unique-learner charts for people counts.")

with course_tab:
    st.subheader("What courses are selected?")
    a, b = st.columns(2)
    with a:
        cat = filtered["CourseCategory"].value_counts().rename_axis("Category").reset_index(name="Enrollments").sort_values("Enrollments")
        fig = px.bar(cat, x="Enrollments", y="Category", orientation="h", text="Enrollments",
                     title="Course category ranking", color="Enrollments", color_continuous_scale="Teal")
        fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, xaxis_title="Enrollments", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    with b:
        level = filtered["CourseLevel"].value_counts().rename_axis("Level").reset_index(name="Enrollments")
        fig = px.bar(level, x="Enrollments", y="Level", orientation="h", text="Enrollments",
                     title="Course level preference", color="Enrollments", color_continuous_scale="Blues")
        fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, xaxis_title="Enrollments", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    a, b = st.columns(2)
    with a:
        ctype = filtered["CourseType"].value_counts().rename_axis("Course type").reset_index(name="Enrollments")
        fig = px.pie(ctype, names="Course type", values="Enrollments", hole=.55, title="Free vs paid enrollment mix")
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        top_courses = filtered.groupby("CourseName").size().sort_values(ascending=False).head(10).sort_values().rename_axis("Course").reset_index(name="Enrollments")
        fig = px.bar(top_courses, x="Enrollments", y="Course", orientation="h", text="Enrollments",
                     title="Top 10 courses by enrollment", color="Enrollments", color_continuous_scale="Teal")
        fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, xaxis_title="Enrollments", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    age_category = pd.crosstab(filtered["AgeGroup"].astype(str), filtered["CourseCategory"])
    st.subheader("Course category by age group")
    fig = px.imshow(age_category, text_auto=True, aspect="auto", title="Age group × course category heatmap",
                    labels={"x": "Course category", "y": "Age group", "color": "Enrollments"})
    fig.update_layout(**PLOT_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

with engagement_tab:
    st.subheader("How learners engage")
    a, b, c = st.columns(3)
    a.metric("Learners with 2+ unique courses", f"{repeat_learners:,}")
    a.metric("Repeat-learner share", f"{repeat_rate:.1f}%")
    b.metric("Highest enrollments by one learner", f"{int(enrollments_per_learner.max()) if not enrollments_per_learner.empty else 0}")
    b.metric("Median enrollments per learner", f"{enrollments_per_learner.median():.1f}" if not enrollments_per_learner.empty else "0")
    c.metric("Unique courses represented", f"{filtered['CourseID'].nunique():,}")
    c.metric("Course categories represented", f"{filtered['CourseCategory'].nunique():,}")

    distribution = enrollments_per_learner.value_counts().sort_index().rename_axis("Enrollments per learner").reset_index(name="Number of learners")
    fig = px.bar(distribution, x="Enrollments per learner", y="Number of learners", text="Number of learners",
                 title="Learner enrollment frequency distribution")
    fig.update_layout(**PLOT_LAYOUT, xaxis_title="Enrollments per learner", yaxis_title="Number of learners")
    st.plotly_chart(fig, use_container_width=True)

    top_people = enrollments_per_learner.sort_values(ascending=False).head(10).rename_axis("UserID").reset_index(name="Enrollments")
    fig = px.bar(top_people, x="Enrollments", y="UserID", orientation="h", text="Enrollments",
                 title="Top 10 learners by enrollment count")
    fig.update_layout(**PLOT_LAYOUT, xaxis_title="Enrollments", yaxis_title="Learner ID")
    st.plotly_chart(fig, use_container_width=True)

with insights_tab:
    st.subheader("Data-driven findings")
    def insight_card(title, message):
        st.markdown(f'<div class="insight"><strong>{title}</strong><br>{message}</div>', unsafe_allow_html=True)

    insight_card("Age group with most enrollments", f"{age_enroll.sort_values('Enrollments', ascending=False).iloc[0]['Age group']} leads among the selected records.")
    insight_card("Most selected category", f"{top_category} has the highest enrollment count in the current filter selection.")
    insight_card("Most selected level", f"{top_level} is the most common course level in the current filter selection.")
    insight_card("Course type", f"{top_type} courses have the most enrollments in the current filter selection.")
    insight_card("Repeat engagement", f"{repeat_rate:.1f}% of learners in the current selection have enrolled in more than one unique course.")

    st.subheader("Recommendations to consider")
    st.markdown(f"""
    - Review demand for **{top_category}** courses and check whether course availability matches learner interest.
    - Maintain clear learning paths across levels, especially where **{top_level}** enrollment is strongest.
    - Compare the **{top_type}** enrollment mix with completion and revenue data before making pricing decisions.
    - Use the age-group and course-category heatmap to identify segments worth investigating further.
    - Investigate highly active learners to understand what supports repeat enrollment.
    """)
    st.info("These recommendations are analytical suggestions, not automated predictions. The workbook contains enrollment data; course completion, learner satisfaction, and revenue should not be inferred unless those fields are available.")

st.markdown("---")
st.caption("EduPro • Descriptive learner analytics • Python · Pandas · Plotly Express · Streamlit")
