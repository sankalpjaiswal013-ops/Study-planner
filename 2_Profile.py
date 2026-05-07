import streamlit as st
from models import User

st.set_page_config(page_title="Profile", page_icon="👤", layout="centered")

if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in from the main page.")
    st.stop()

st.title("User Profile 👤")

# Load current user using DB Abstraction
user = User.find_by_id(st.session_state.user_id)

if user:
    st.markdown("""
    <style>
        .profile-card {
            background-color: #f8fafc;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-top: 5px solid #7c3aed;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
    
    # Showcase Encapsulation via getter
    st.write(f"**Current Name:** {user.name}")
    st.write(f"**Email:** {user.email}")
    
    st.divider()
    
    st.subheader("Edit Profile")
    with st.form("edit_profile"):
        new_name = st.text_input("New Name", value=user.name)
        new_password = st.text_input("New Password", type="password", help="Leave blank to keep current password")
        
        if st.form_submit_button("Update"):
            try:
                # Showcase Encapsulation via setter which throws ValueError on empty
                user.name = new_name
                
                if new_password:
                    user.set_password(new_password)
                    
                user.save()
                st.session_state.user_name = user.name
                st.success("Profile updated successfully!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
                
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("User not found.")
