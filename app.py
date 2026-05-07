import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

from database import authenticate_user, create_user, get_db_connection, get_setting
from utils import get_streak

st.set_page_config(page_title="AI Study Planner", page_icon="🧠", layout="wide")

# Theme setup (basic CSS injection for styling)
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #38BDF8; }
    .metric-label { font-size: 1rem; color: #94A3B8; }
</style>
""", unsafe_allow_html=True)

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# --- AUTHENTICATION ---
if not st.session_state.user_id:
    st.title("🧠 AI Study Planner")
    st.write("Welcome! Please log in or sign up to access your personalized study dashboard.")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            l_email = st.text_input("Email")
            l_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = authenticate_user(l_email, l_pass)
                if user:
                    st.session_state.user_id = user["id"]
                    st.session_state.user_name = user["name"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
                    
    with tab2:
        with st.form("signup_form"):
            s_name = st.text_input("Full Name")
            s_email = st.text_input("Email")
            s_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Sign Up"):
                if create_user(s_name, s_email, s_pass):
                    st.success("Account created! You can now log in.")
                else:
                    st.error("Email already exists.")
                    
    st.stop()

# --- MODULE 6 & 7: DASHBOARD & REMINDERS ---
user_id = st.session_state.user_id
st.title(f"Welcome back, {st.session_state.user_name}! 👋")

# Motivational Quote
quotes = [
    "The secret of getting ahead is getting started.",
    "It always seems impossible until it's done.",
    "Don't watch the clock; do what it does. Keep going.",
    "Success is the sum of small efforts, repeated day-in and day-out."
]
st.info(f"💡 {random.choice(quotes)}")

# --- SMART REMINDERS ---
st.subheader("🔔 Smart Reminders")
conn = get_db_connection()
c = conn.cursor()
today_str = datetime.now().date().strftime("%Y-%m-%d")

# Tasks due today or overdue
c.execute("SELECT topic, subject, due_date FROM tasks WHERE user_id=? AND completed=0 ORDER BY due_date ASC LIMIT 5", (user_id,))
pending_tasks = c.fetchall()

if pending_tasks:
    for pt in pending_tasks:
        if pt["due_date"] < today_str:
            st.error(f"⚠️ **OVERDUE:** {pt['topic']} ({pt['subject']}) - was due {pt['due_date']}")
        elif pt["due_date"] == today_str:
            st.warning(f"🕒 **DUE TODAY:** {pt['topic']} ({pt['subject']})")
        else:
            st.success(f"📅 **Upcoming:** {pt['topic']} ({pt['subject']}) - due {pt['due_date']}")
else:
    st.write("No pending tasks. Great job!")

st.divider()

# --- PROGRESS DASHBOARD ---
st.subheader("📈 Progress Dashboard")

# Calculate Metrics
# 1. Total study time this week
week_ago = (datetime.now().date() - timedelta(days=7)).strftime("%Y-%m-%d")
c.execute("SELECT SUM(hours_studied) as total FROM study_log WHERE user_id=? AND date >= ?", (user_id, week_ago))
weekly_hours = c.fetchone()["total"] or 0.0

# 2. Tasks completed today
c.execute("SELECT COUNT(*) as count FROM tasks WHERE user_id=? AND completed=1 AND due_date=?", (user_id, today_str)) # Note: using due_date as proxy for completion date if no completed_at
tasks_today = c.fetchone()["count"]

# 3. Streak
streak = get_streak(user_id)

# 4. Overall Progress
c.execute("SELECT COUNT(*) as total, SUM(completed) as done FROM tasks WHERE user_id=?", (user_id,))
row = c.fetchone()
total_tasks = row["total"] or 0
done_tasks = row["done"] or 0
progress_pct = round((done_tasks / total_tasks * 100) if total_tasks > 0 else 0)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{weekly_hours:.1f}h</div><div class="metric-label">Studied This Week</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{tasks_today}</div><div class="metric-label">Tasks Done Today</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{streak} 🔥</div><div class="metric-label">Day Streak</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{progress_pct}%</div><div class="metric-label">Overall Progress</div></div>', unsafe_allow_html=True)

st.write("")

# Charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("**Study Hours (Last 14 Days)**")
    two_weeks_ago = (datetime.now().date() - timedelta(days=14)).strftime("%Y-%m-%d")
    c.execute("SELECT date, SUM(hours_studied) as hours FROM study_log WHERE user_id=? AND date >= ? GROUP BY date ORDER BY date", (user_id, two_weeks_ago))
    log_data = c.fetchall()
    
    if log_data:
        df_logs = pd.DataFrame([dict(row) for row in log_data])
        fig_line = px.line(df_logs, x="date", y="hours", markers=True, line_shape="spline", color_discrete_sequence=["#38BDF8"])
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No study logs yet. Use the Pomodoro timer to start tracking!")

with chart_col2:
    st.write("**Time Distribution across Subjects**")
    c.execute("SELECT subject, SUM(hours_studied) as hours FROM study_log WHERE user_id=? GROUP BY subject", (user_id,))
    dist_data = c.fetchall()
    
    if dist_data:
        df_dist = pd.DataFrame([dict(row) for row in dist_data])
        fig_pie = px.pie(df_dist, names="subject", values="hours", hole=0.4, color_discrete_sequence=px.colors.sequential.Tealgrn)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data available.")

conn.close()
