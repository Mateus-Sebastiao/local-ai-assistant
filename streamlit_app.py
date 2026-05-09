import streamlit as st 
import httpx
from core.config import settings

import uuid

st.set_page_config(page_title="DevOps AI Assistant", layout="centered")
st.title('Senior DevOps Assistant v1')

# Initialize visual memory only
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Create a persistent client to store cookies automatically
    st.session_state.client = httpx.Client(base_url=settings.API_URL, timeout=None)

# Render history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("How Can I Help You...?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            with st.session_state.client.stream(
                "POST", 
                "/api/analyze/stream",
                json={"user_prompt": prompt}
            ) as response:
                
                if response.status_code == 200:
                    for chunk in response.iter_text():
                        full_response += chunk
                        placeholder.markdown(full_response + "▌")
                    
                    placeholder.markdown(full_response)
                else:
                    st.error(f"API Error: {response.status_code}")
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Connection Error: {e}")