import streamlit as st
import requests
import json
import time
from pathlib import Path

# --- Configuration ---
API_BASE_URL = "http://localhost:8000/api/v1"
STATIC_URL = "http://localhost:8000/static"

st.set_page_config(
    page_title="Multi-Modal REFRAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    .stTextInput>div>div>input {
        background-color: #262730;
        color: white;
        border-radius: 8px;
        border: 1px solid #4CAF50;
    }
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex
    }
    .chat-message.user {
        background-color: #2b313e
    }
    .chat-message.bot {
        background-color: #475063
    }
    .source-image {
        border: 2px solid #4CAF50;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing_tasks" not in st.session_state:
        st.markdown(prompt)
    
    # Get Bot Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Prepare payload
                payload = {"query": prompt, "top_k": 5}
                
                response = requests.post(f"{API_BASE_URL}/query", json=payload)
                
                if response.status_code == 200:
                    res_data = response.json()
                    answer = res_data["answer"]
                    sources = res_data["sources"]
                    query_id = res_data.get("query_id", "")
                    
                    st.markdown(answer)
                    
                    # Save context
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources,
                        "query_id": query_id
                    })
                    
                    # Show sources immediately
                    with st.expander("📚 View Sources & Images"):
                        for idx, source in enumerate(sources, 1):
                            st.markdown(f"### Source {idx}: {source['source_file']}")
                            st.caption(f"Score: {source['score']:.2f} | Type: {source.get('chunk_type', 'text')}")
                            
                            # Display image if available
                            if source.get('image_path'):
                                try:
                                    img_path = Path(source['image_path'])
                                    source_id = img_path.parent.parent.name
                                    filename = img_path.name
                                    image_url = f"{STATIC_URL}/images/{source_id}/{filename}"
                                    
                                    st.image(image_url, caption=f"Page {source.get('metadata', {}).get('page_number', 'N/A')}", use_container_width=True)
                                except Exception as e:
                                    st.warning(f"Could not load image: {e}")
                            
                            # Show text content
                            with st.container():
                                st.text_area(
                                    "Content",
                                    source['chunk_text'][:300] + ("..." if len(source['chunk_text']) > 300 else ""),
                                    height=100,
                                    key=f"source_{query_id}_{idx}",
                                    disabled=True
                                )
                            st.markdown("---")
                            
                else:
                    st.error(f"Error from backend: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")
