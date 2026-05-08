import streamlit as st 
import httpx
from core.config import settings

import uuid

st.set_page_config(page_title="DevOps AI Assistant", layout="centered")
st.title('Senior DevOps Assistant v1')

# if prompt := st.chat_input("Ask about Kubernetes, Cilium, or DevOps..."):
#     st.chat_message("user").write(prompt)

#     with st.spinner("The Engineer is thinking..."):
#         try:
#             params = {"user_prompt": prompt}
#             response = httpx.post(f"{settings.API_URL}/api/analyze", params=params, timeout=None)

#             if response.status_code == 200:
#                 data = response.json()
#                 st.chat_message("assistant").write(data['analysis'])
#             else:
#                 st.error(f"Error: {response.status_code}")
#         except Exception as e:
#             st.error(f"Connection failed: {e}")

# Initialize visual memory only
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Create a persistent client to store cookies automatically
    st.session_state.client = httpx.Client(base_url=settings.API_URL)

# Render history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("How Can I Help You...?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("Thinking..."):
        try:
            json_data = {"user_prompt": prompt}
            
            # Use the persistent client to handle the session cookie
            response = st.session_state.client.post("/api/analyze", json=json_data, timeout=None)

            if response.status_code == 200:
                data = response.json()
                st.session_state.messages.append({"role": "assistant", "content": data['analysis']})
                st.chat_message("assistant").write(data['analysis'])
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Connection failed: {e}")