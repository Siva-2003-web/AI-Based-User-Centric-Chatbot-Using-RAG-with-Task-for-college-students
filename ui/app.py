import streamlit as st

st.set_page_config(page_title="RAG + Automation Chatbot", page_icon="🤖", layout="centered")

st.title("RAG + Automation Chatbot")
st.caption("Placeholder UI — wire to FastAPI backend")

user_input = st.text_area("Your message", height=120)

if st.button("Send"):
    if not user_input.strip():
        st.warning("Please enter a message first.")
    else:
        # TODO: call FastAPI /chat endpoint with conversation history
        st.info(
            "Backend not connected yet. Add API call to /chat and display reply, sources, actions."
        )
