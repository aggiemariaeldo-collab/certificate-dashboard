"""
Student Certificate & Achievement Dashboard
CHRIST (Deemed to be University) - MCA411-2 Python Programming, Component 3

Run with:  streamlit run app.py
"""
import os
import random
from datetime import date, datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Certificate Tracker", page_icon="🏆", layout="wide")
plt.style.use("dark_background")              # dark charts to match the dark app
plt.rcParams["savefig.transparent"] = True

# =====================================================================
# 1. SETTINGS
# =====================================================================
DATA_FILE = "data/certificates.csv"
COLUMNS = ["student_id", "student_name", "department", "title", "category", "level",
           "position", "issue_date", "expiry_date", "status", "points", "review_days"]

DEPARTMENTS = ["MCA", "MBA", "BCA", "BBA", "B.Com", "BSc CS", "MSc Data Science"]
CATEGORIES = ["Course Completion", "Hackathon", "Competition", "Workshop",
              "Internship", "Publication", "Sports", "Cultural"]
LEVELS = ["College", "University", "State", "National", "International"]
POSITIONS = ["Participant", "Runner-up", "Winner"]
STATUSES = ["Verified", "Pending", "Rejected"]

# points = points for the level + bonus for the position
LEVEL_POINTS = {"College": 5, "University": 10, "State": 15, "National": 25, "International": 40}
POSITION_BONUS = {"Participant": 0, "Runner-up": 5, "Winner": 10}

PERIODS = {"3M": 90, "6M": 180, "12M": 365, "24M": 730}    # button -> number of days
PURPLE = "#6C6CE5"
PIE_COLORS = ["#6C6CE5", "#4FA58F", "#E0762F", "#D0589A", "#4A90E2", "#C0902A", "#8E7CC3"]


def points_for(level, position):
    return LEVEL_POINTS[level] + POSITION_BONUS[position]


# =====================================================================
# 2. SAMPLE DATA  (created only once, the first time the app runs)
# =====================================================================
def make_sample_data():
    random.seed(7)
    first_names = ["Aarav", "Ananya", "Rohan", "Sneha", "Karthik", "Meera", "Vikram", "Divya", "Arjun",
                   "Priya", "Nikhil", "Aditi", "Rahul", "Kavya", "Siddharth", "Ishita", "Varun", "Pooja",
                   "Harsh", "Neha", "Joel", "Tanya", "Sanjay", "Riya", "Mohan"]
    last_names = ["Sharma", "Nair", "Reddy", "Iyer", "Menon", "Das", "Gupta", "Thomas",
                  "Kumar", "Joseph", "Rao", "Patel", "Singh", "Mathew", "Pillai"]
    titles = ["Python Course", "SQL Course", "Hackathon Finalist", "Coding Contest", "AI Workshop",
              "Data Analyst Internship", "Research Paper", "Cricket Tournament", "Dance Competition"]

    rows = []
    for i in range(60):                                   # 60 students
        student_id = str(2541000 + i)
        student_name = first_names[i % 25] + " " + last_names[i % 15]
        department = random.choice(DEPARTMENTS)
        for _ in range(random.randint(3, 15)):            # 3 to 15 certificates each
            category = random.choice(CATEGORIES)
            level = random.choice(LEVELS)
            position = "Participant"
            if category in ["Hackathon", "Competition", "Sports", "Cultural"]:
                position = random.choice(POSITIONS)
            days_ago = random.randint(0, random.choice([180, 365, 729]))
            issue_date = date.today() - timedelta(days=days_ago)

            status = random.choice(["Verified"] * 8 + ["Pending", "Rejected"])
            if days_ago > 45 and status == "Pending":     # old certificates are already reviewed
                status = "Verified"
            review_days = ""
            if status != "Pending":
                review_days = random.randint(2, 20)
            expiry_date = ""
            if category == "Course Completion" and random.random() < 0.5:
                expiry_date = str(issue_date + timedelta(days=random.randint(300, 800)))

            rows.append([student_id, student_name, department, random.choice(titles), category, level,
                         position, str(issue_date), expiry_date, status,
                         points_for(level, position), review_days])
    return pd.DataFrame(rows, columns=COLUMNS)


if not os.path.exists(DATA_FILE):
    os.makedirs("data", exist_ok=True)
    make_sample_data().to_csv(DATA_FILE, index=False)

# =====================================================================
# 3. PAGE TOP: title, live time, period buttons, tabs
# =====================================================================
st.title("🏆 Certificates & Achievements")
st.caption("🟢 Live · updated " + datetime.now().strftime("%H:%M:%S"))

period = st.radio("Time period", list(PERIODS), horizontal=True)
days = PERIODS[period]

tab_over, tab_students, tab_verify = st.tabs(
    ["📈 Overview", "👩‍🎓 Students", "✅ Verification"])

# =====================================================================
# 4. ADD CERTIFICATE  (written first so the new row is saved BEFORE the data is loaded)
# =====================================================================
with tab_add:
    st.subheader("Add a new certificate")
    with st.form("add_form", clear_on_submit=True):
        student_id = st.text_input("Register number")
        student_name = st.text_input("Student name")
        department = st.selectbox("Department", DEPARTMENTS)
        title = st.text_input("Certificate title")
        category = st.selectbox("Category", CATEGORIES)
        level = st.selectbox("Level", LEVELS)
        position = st.selectbox("Position", POSITIONS)
        issue_date = st.date_input("Issue date", value=date.today())
        save = st.form_submit_button("Save certificate")

    if save:
        if student_id == "" or student_name == "" or title == "":
            st.error("Register number, name and title are required.")
        else:
            points = points_for(level, position)
            new_row = pd.DataFrame([[student_id, student_name, department, title, category, level,
                                     position, str(issue_date), "", "Pending", points, ""]],
                                   columns=COLUMNS)
            new_row.to_csv(DATA_FILE, mode="a", header=False, index=False)   # append to the CSV
            st.success(f"Saved! {student_name} earned {points} points (status: Pending).")

    st.caption("Points = level points + position bonus. "
               "Level: " + str(LEVEL_POINTS) + "  Bonus: " + str(POSITION_BONUS))

# =====================================================================
# 5. LOAD DATA + FILTERS  (sidebar)
# =====================================================================
df = pd.read_csv(DATA_FILE, dtype={"student_id": str})
df["issue_date"] = pd.to_datetime(df["issue_date"])
df["expiry_date"] = pd.to_datetime(df["expiry_date"])

st.sidebar.header("Filters")
dept = st.sidebar.multiselect("Department", DEPARTMENTS)
cat = st.sidebar.multiselect("Category", CATEGORIES)
level_filter = st.sidebar.multiselect("Level", LEVELS)
status = st.sidebar.multiselect("Verification status", STATUSES, default=["Verified", "Pending"])

data_any = df.copy()                                  # filters except status
if dept:
    data_any = data_any[data_any["department"].isin(dept)]
if cat:
    data_any = data_any[data_any["category"].isin(cat)]
if level_filter:
    data_any = data_any[data_any["level"].isin(level_filter)]

data = data_any
if status:
    data = data_any[data_any["status"].isin(status)]  # all filters


# rows issued in the last `start` days, up to `end` days ago
today = pd.Timestamp.today().normalize()


def last_days(d, start, end=0):
    after = d["issue_date"] > today - pd.Timedelta(days=start)
    before = d["issue_date"] <= today - pd.Timedelta(days=end)
    return d[after & before]


cur = last_days(data, days)                # selected period
prev = last_days(data, 2 * days, days)     # the period before it (to show the change)
cur_any = last_days(data_any, days)        # selected period, any status

st.sidebar.download_button("⬇ Download data (CSV)", cur.to_csv(index=False), "certificates.csv")

if cur.empty:
    st.warning("No certificates for these filters in this period. Change the filters or the period.")
    st.stop()


def percent_change(now, before):
    if before == 0:
        return None
    return f"{(now - before) / before * 100:+.1f}%"


# =====================================================================
# 6. OVERVIEW PAGE
# =====================================================================
with tab_over:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Certificates", len(cur), percent_change(len(cur), len(prev)))
    k2.metric("Total points", int(cur["points"].sum()),
              percent_change(cur["points"].sum(), prev["points"].sum()))
    k3.metric("Active students", cur["student_id"].nunique(),
              percent_change(cur["student_id"].nunique(), prev["student_id"].nunique()))
    verified_rate = (cur["status"] == "Verified").mean() * 100
    rate_change = None
    if len(prev) > 0:
        rate_change = f"{verified_rate - (prev['status'] == 'Verified').mean() * 100:+.1f} pts"
    k4.metric("Verified rate", f"{verified_rate:.0f}%", rate_change)

    left, right = st.columns(2)

    # LINE chart - certificates per month
    with left:
        per_month = cur.groupby(cur["issue_date"].dt.strftime("%Y-%m")).size()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.plot(per_month.index, per_month.values, marker="o", color=PURPLE)
        ax.set_title("Certificates per month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Certificates")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # BAR chart - certificates by category
    with right:
        by_category = cur["category"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.bar(by_category.index, by_category.values, color=PURPLE)
        ax.set_title("Certificates by category")
        ax.set_ylabel("Certificates")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

    left, right = st.columns(2)

    # PIE chart - points by level
    with left:
        by_level = cur.groupby("level")["points"].sum()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.pie(by_level.values, labels=by_level.index, autopct="%1.0f%%", colors=PIE_COLORS)
        ax.set_title("Points by level")
        st.pyplot(fig)

    # HISTOGRAM - how many points each student has
    with right:
        points_per_student = cur.groupby("student_id")["points"].sum()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.hist(points_per_student.values, bins=10, color=PURPLE, edgecolor="black")
        ax.set_title("Distribution of points per student")
        ax.set_xlabel("Points")
        ax.set_ylabel("Number of students")
        st.pyplot(fig)

    # TABLE - top 10 students
    st.subheader("Top 10 students")
    top10 = cur.groupby("student_name").agg(Certificates=("title", "count"), Points=("points", "sum"))
    st.dataframe(top10.sort_values("Points", ascending=False).head(10))

# =====================================================================
# 7. STUDENTS PAGE
# =====================================================================
with tab_students:
    left, right = st.columns(2)

    # BAR chart - points by department
    with left:
        by_dept = cur.groupby("department")["points"].sum().sort_values()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.barh(by_dept.index, by_dept.values, color=PURPLE)
        ax.set_title("Points by department")
        ax.set_xlabel("Points")
        st.pyplot(fig)

    # PIE chart - certificates by department
    with right:
        dept_count = cur["department"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.pie(dept_count.values, labels=dept_count.index, autopct="%1.0f%%", colors=PIE_COLORS)
        ax.set_title("Certificates by department")
        st.pyplot(fig)

    # certificates that expire in the next 90 days
    st.subheader("Certificates expiring in the next 90 days")
    soon = data[(data["expiry_date"] >= today) & (data["expiry_date"] <= today + pd.Timedelta(days=90))]
    if soon.empty:
        st.info("Nothing expires soon.")
    else:
        soon = soon.sort_values("expiry_date")
        st.dataframe(soon[["student_name", "title", "expiry_date"]], hide_index=True)

    # all students with search
    st.subheader("All students")
    search = st.text_input("Search by student name or department")
    students = data.groupby(["student_id", "student_name", "department"]).agg(
        Certificates=("title", "count"), Points=("points", "sum")).reset_index()
    if search:
        by_name = students["student_name"].str.contains(search, case=False, regex=False)
        by_dept = students["department"].str.contains(search, case=False, regex=False)
        students = students[by_name | by_dept]
    st.dataframe(students.sort_values("Points", ascending=False), hide_index=True)

# =====================================================================
# 8. VERIFICATION PAGE
# =====================================================================
with tab_verify:
    submitted = len(cur_any)
    n_verified = int((cur_any["status"] == "Verified").sum())
    n_pending = int((cur_any["status"] == "Pending").sum())
    n_rejected = int((cur_any["status"] == "Rejected").sum())
    reviewed = n_verified + n_rejected
    avg_days = pd.to_numeric(cur_any["review_days"]).mean()
    if pd.isna(avg_days):
        avg_days = 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Submitted", submitted)
    k2.metric("Pending review", n_pending)
    k3.metric("Verification rate", f"{n_verified / max(reviewed, 1) * 100:.0f}%")
    k4.metric("Avg. review time", f"{avg_days:.0f} days")

    # progress bar - this month's goal
    st.subheader("Monthly goal")
    target = st.number_input("Target (verified certificates this month)", min_value=1, value=20)
    this_month = today.replace(day=1)
    done = len(data_any[(data_any["status"] == "Verified") & (data_any["issue_date"] >= this_month)])
    st.progress(min(done / target, 1.0), text=f"{done} of {target} verified this month")

    left, right = st.columns(2)

    # PIE chart - status
    with left:
        by_status = cur_any["status"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.pie(by_status.values, labels=by_status.index, autopct="%1.0f%%", colors=PIE_COLORS)
        ax.set_title("Verification status")
        st.pyplot(fig)

    # BAR chart - verified certificates per month
    with right:
        verified = cur_any[cur_any["status"] == "Verified"]
        verified_per_month = verified.groupby(verified["issue_date"].dt.strftime("%Y-%m")).size()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.bar(verified_per_month.index, verified_per_month.values, color=PURPLE)
        ax.set_title("Verified certificates per month")
        ax.set_ylabel("Certificates")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # HISTOGRAM - how many days a review takes
    review_days = pd.to_numeric(cur_any["review_days"]).dropna()
    if len(review_days) > 0:
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.hist(review_days, bins=10, color=PURPLE, edgecolor="black")
        ax.set_title("Days taken to review a certificate")
        ax.set_xlabel("Days")
        ax.set_ylabel("Certificates")
        st.pyplot(fig)
