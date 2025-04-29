from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
# from langchain.agents import create_tool_calling_agent, AgentExecutor
import streamlit as st
import re
import os
# from tools import search_tool,wiki_tool,save_tool,language_tool, explain_tool, analyze_tool, fix_tool

load_dotenv()

# Initialize the LLM
llm = ChatGroq(
    model="Llama3-70b-8192",
    temperature=0,
    groq_api_key=os.getenv("API_KEY")
)

st.title("Adventure with Choices 🎯")

# Set up session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """You are a creative text adventure game master. 
After each event, suggest exactly 3 options for what the player can do next. Have a maximum of 5-6 endings consisting of good and bad endings which depend on the user based on his choices. 
Clearly list them as: 1., 2., 3. Don't skip this."""}
    ]

if "choices" not in st.session_state:
    st.session_state.choices = ["Explore the cave", "Climb the mountain", "Swim across the river"]
if "choice_made" not in st.session_state:
    st.session_state.choice_made = False
if "game_over" not in st.session_state:
    st.session_state.game_over = False

def reset_game():
    st.session_state.messages = [
        {"role": "system", "content": """You are a creative text adventure game master. 
After each event, suggest exactly 3 options for what the player can do next. 
Have a maximum of 5-6 endings consisting of good and bad endings based on the user's choices. 
Clearly list them as: 1., 2., 3. Don't skip this."""}
    ]
    st.session_state.choices = ["Explore the cave", "Climb the mountain", "Swim across the river"]
    st.session_state.choice_made = False
    st.session_state.game_over = False

if not st.session_state.choice_made and not st.session_state.game_over:
    choice = st.radio("What do you want to do?", st.session_state.choices)
    if st.button("Confirm Choice"):
        # Add user choice to conversation
        st.session_state.messages.append({"role": "user", "content": f"The player chose: {choice}. What happens next?"})

        # Send whole message history
        response = llm.invoke(st.session_state.messages)

        # Get LLM's story response
        ai_content = response.content
        st.session_state.messages.append({"role": "assistant", "content": ai_content})
        st.session_state.last_ai_reply = ai_content
        # Display the response
        # st.markdown(f"**Game Master:** {ai_content}")

        # Parse new choices from the LLM output
        
        if any(kw in ai_content.lower() for kw in ["the end", "bad ending", "good ending", "game over"]):
            st.session_state.game_over = True
        else:
            new_choices = re.findall(r"\d\.\s*(.+)", ai_content)
            if new_choices:
                st.session_state.choices = new_choices
            # fallback choices if parsing fails
            else:
                st.session_state.choices = ["Continue forward", "Return to village", "Search the area"]
        
        st.rerun()

elif st.session_state.choice_made and not st.session_state.game_over:
    st.markdown(f"**Game Master:** {st.session_state.last_ai_reply}")
    st.session_state.choice_made = False

if st.session_state.game_over:
    st.markdown(f"**Game Master:** {st.session_state.last_ai_reply}")
    st.success("🎉 You reached an ending!")

    if st.button("🔄 Retry Adventure"):
        reset_game()
        st.rerun()
    if st.button("❌ Exit"):
        st.stop()

st.divider()
st.header("Story so far:")
for msg in st.session_state.messages[1:]:  # skip system message
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Game Master:** {msg['content']}")