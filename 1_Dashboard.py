import streamlit as st
import pandas as pd
from models import Task, GeneralTask, AssignmentTask, ExamPrepTask

st.set_page_config(page_title="Dashboard", page_icon="📝", layout="wide")

if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in from the main page to access your dashboard.")
    st.stop()

st.title(f"Dashboard 📊")

# CSS for a beautiful look
st.markdown("""
<style>
    .task-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 5px solid #2563eb;
    }
    .task-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 8px;
    }
    .task-meta {
        font-size: 0.875rem;
        color: #6b7280;
        margin-bottom: 12px;
    }
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 8px;
    }
    .badge-high { background-color: #fee2e2; color: #dc2626; }
    .badge-medium { background-color: #fef3c7; color: #d97706; }
    .badge-low { background-color: #e0e7ff; color: #4f46e5; }
    
    .badge-todo { background-color: #f3f4f6; color: #374151; }
    .badge-inprogress { background-color: #dbeafe; color: #1e40af; }
    .badge-completed { background-color: #dcfce3; color: #166534; }
</style>
""", unsafe_allow_html=True)

user_id = st.session_state.user_id

# ----------------- ADD TASK SECTION -----------------
with st.expander("➕ Add New Task", expanded=False):
    with st.form("add_task_form"):
        title = st.text_input("Title")
        desc = st.text_area("Description")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            status = st.selectbox("Status", ["To Do", "In Progress", "Completed"])
        with col2:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        with col3:
            task_type = st.selectbox("Task Type", ["General", "Assignment", "Exam Prep"])
            
        # Extra fields based on type
        # Note: In a Streamlit form, we can't dynamically show/hide inputs based on another selectbox 
        # seamlessly without reruns, so we'll collect all optional fields and use the relevant one.
        st.caption("Extra details (fill depending on task type)")
        ecol1, ecol2 = st.columns(2)
        with ecol1:
            subject = st.text_input("Subject (for Assignment)")
        with ecol2:
            exam_date = st.date_input("Exam Date (for Exam Prep)")
            
        submitted = st.form_submit_button("Save Task")
        
        if submitted:
            if not title:
                st.error("Title is required!")
            else:
                new_task = None
                if task_type == "General":
                    new_task = GeneralTask(user_id, title, desc, status, priority)
                elif task_type == "Assignment":
                    new_task = AssignmentTask(user_id, title, desc, status, priority, subject)
                elif task_type == "Exam Prep":
                    new_task = ExamPrepTask(user_id, title, desc, status, priority, str(exam_date))
                
                if new_task:
                    new_task.save()
                    st.success("Task added successfully!")
                    st.rerun()

# ----------------- DISPLAY TASKS -----------------
st.divider()
tasks = Task.get_user_tasks(user_id)

if not tasks:
    st.info("No tasks found. Create one above!")
else:
    # Top controls for filtering
    colA, colB = st.columns([1, 1])
    with colA:
        filter_status = st.selectbox("Filter by Status", ["All", "To Do", "In Progress", "Completed"])
    with colB:
        filter_type = st.selectbox("Filter by Type", ["All", "General", "Assignment", "Exam Prep"])
        
    filtered_tasks = tasks
    if filter_status != "All":
        filtered_tasks = [t for t in filtered_tasks if t.status == filter_status]
    if filter_type != "All":
        filtered_tasks = [t for t in filtered_tasks if t.get_task_type() == filter_type]
        
    st.write(f"Showing **{len(filtered_tasks)}** tasks.")
    
    for t in filtered_tasks:
        # Badges CSS classes
        p_class = f"badge-{t.priority.lower()}"
        s_class = f"badge-{t.status.lower().replace(' ', '')}"
        
        # Display specific info using polymorphism
        extra_info = ""
        if isinstance(t, AssignmentTask):
            extra_info = f" | 📘 Subject: {t.subject}"
        elif isinstance(t, ExamPrepTask):
            extra_info = f" | 📅 Exam: {t.exam_date}"
            
        st.markdown(f"""
        <div class="task-card">
            <div class="task-title">{t.title}</div>
            <div class="task-meta">
                <span class="badge {p_class}">{t.priority}</span>
                <span class="badge {s_class}">{t.status}</span>
                <span style="font-weight:600; color:#4b5563;">{t.get_task_type()}</span>
                {extra_info}
            </div>
            <div style="color: #4b5563; font-size: 0.95rem;">{t.description}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Delete button using Streamlit native widgets
        if st.button("Delete Task", key=f"del_{t.id}"):
            t.delete()
            st.rerun()
