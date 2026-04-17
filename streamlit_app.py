import streamlit as st 
import httpx
from core.config import settings

st.set_page_config(page_title="DevOps AI Assistant", layout="centered")
st.title('Senior DevOps Assistant v1')

if prompt := st.chat_input("Ask about Kubernetes, Cilium, or DevOps..."):
    st.chat_message("user").write(prompt)

    with st.spinner("The Engineer is thinking..."):
        try:
            params = {"user_prompt": prompt}
            response = httpx.post(f"{settings.API_URL}/api/analyze", params=params, timeout=None)

            if response.status_code == 200:
                data = response.json()
                st.chat_message("assistant").write(data['analysis'])
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Connection failed: {e}")
