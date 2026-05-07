import streamlit as st
from ai_helper import generate_ai_response

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in from the main page.")
    st.stop()

user_id = st.session_state.user_id

st.title("🤖 AI Study Assistant")
st.write("Your personal tutor powered by AI. It knows your weak subjects and pending tasks!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI Study Assistant. How can I help you today?"}
    ]

# Display quick actions
st.write("### Quick Actions")
col1, col2, col3, col4 = st.columns(4)

prompt_to_send = None

with col1:
    if st.button("Analyze my weak subjects", use_container_width=True):
        prompt_to_send = "Analyze my weak subjects and give me specific improvement tips."
with col2:
    if st.button("What should I study today?", use_container_width=True):
        prompt_to_send = "What should I study today based on urgency and weakness?"
with col3:
    if st.button("Make me a study plan", use_container_width=True):
        prompt_to_send = "Make me a study plan for today based on my available hours."
with col4:
    if st.button("Motivate me", use_container_width=True):
        prompt_to_send = "Motivate me with some encouraging words!"

st.divider()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process prompt (either from button or chat input)
user_input = st.chat_input("Ask me anything about your studies...")

if user_input or prompt_to_send:
    final_prompt = prompt_to_send if prompt_to_send else user_input
    
    # Display user message in chat message container
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = generate_ai_response(user_id, final_prompt, st.session_state.messages[:-1])
        response = st.write_stream(stream)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
