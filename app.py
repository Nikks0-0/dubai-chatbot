import streamlit as st
import requests

st.set_page_config(page_title="Dubai Trip Planner", layout="wide", initial_sidebar_state="auto")
st.markdown(
    """
    <style>
    .stChatMessage {margin-bottom: 1.5rem;}
    .stChatInput {margin-top: 2rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌴 Dubai Trip Planner — AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hi! I’m your Dubai travel planner bot. When are you planning your trip to Dubai?"}
    ]
if "state" not in st.session_state:
    st.session_state.state = {}

def send_to_backend(user_input):
    res = requests.post(
        "http://localhost:8000/chat",
        json={"user_id": "user1", "input": user_input}
    )
    return res.json()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_prompt = st.chat_input("Type your message...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    state = st.session_state.state
    import re
    # Step logic
    if state.get("step") == "ask_dates" or not state:
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", user_prompt)
        user_input = {}
        if len(dates) >= 2:
            user_input["start_date"] = dates[0]
            user_input["end_date"] = dates[1]
        else:
            user_input = {"message": user_prompt}
    elif state.get("step") == "ask_budget":
        budget = re.findall(r"\d+", user_prompt)
        user_input = {"budget": int(budget[0])} if budget else {"message": user_prompt}
    else:
        user_input = {"message": user_prompt}

    response = send_to_backend(user_input)
    st.session_state.state = response["state"]
    st.session_state.messages.append({"role": "assistant", "content": response["reply"]})
    st.rerun()

with st.sidebar:
    st.header("🎨 Theme & Info")
    st.info("Switch between light and dark mode in the sidebar settings.")
    st.markdown("Made with ❤️ using OpenAI, Amadeus, and Streamlit.")
