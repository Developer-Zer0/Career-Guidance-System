from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import shelve
import random
from time import sleep

from student import Student
from schema import Schema, orig_schema, schema_limit

load_dotenv()
st.title("Character Creation Demo")

USER_AVATAR = "👤"
# BOT_AVATAR_LIST = "🧑🧑‍🦱🧑‍🦰👱🧑‍🦳🧑‍🦲🧔🧓👳👧👩👩‍🦱👩‍🦰👱‍♀️👩‍🦳🧔‍♀️👵🧕👨‍🦰"
# BOT_AVATAR = random.choice(BOT_AVATAR_LIST)
BOT_AVATAR = "🧑‍🦲"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Ensure openai_model is initialized in session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"


# Load chat history from shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        # return db.get("messages", [])
        return []


# Save chat history to shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

sys_p = """
You have to roleplay a student attending a career counselling session. Do not generate a dialogue, the user will be asking the questions as a counsellor.
Initially you will not have any personality. Start generating new information about the student depending on the questions asked by the counsellor. 
The counsellor will have a dialogue with you and you must answer the questions while being consistent with the information you have generated previously. 
If a question is asked which requires information not included in the personality, you must generate a response which is consistent with the personality and remember it for future reference.
"""

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()
    st.session_state.messages.append({"role": "system", "content": sys_p})
    st.session_state.schema = Schema(orig_schema, schema_limit)
    st.session_state.s = Student(st.session_state.schema)
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')


# Sidebar with a button to delete chat history
with st.sidebar:
    detected_fields_container = st.empty()
    detected_fields_container.write('Detected Dialogue Acts Displayed Here')
    percent_container = st.empty()
    percent_container.write('Schema Progress Displayed Here')
    # if st.button("Delete Chat History"):
    #     st.session_state.messages = []
    #     save_chat_history([])

with st.sidebar:
    json_container = st.empty()
    json_container.write(st.session_state.s.schema.get_schema())
    # with st.container():
    #     st.json(s.schema.get_schema())

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        avatar = USER_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    elif message['role'] == 'assistant':
        avatar = BOT_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("Ask Questions or continue dialogue"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        sleep(5)
        full_response = ""
        # full_response = st.session_state.s.respond(prompt)
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=st.session_state["messages"],
            stream=True,
        ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "|")

        st.session_state.s.update_schema(prompt, None, full_response, None)

        detected_fields_container.empty()
        detected_fields_container.write(st.session_state.s.last_detected_fields)
        percent_container.empty()
        percent_container.write(f'{int(st.session_state.s.schema.progress_percent())}%')
        json_container.empty()
        json_container.write(st.session_state.s.schema.get_schema())
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)