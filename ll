import streamlit as st

def local_css(style):
    st.markdown(f'<style>{style}</style>', unsafe_allow_html=True)

# مثال لتنسيق البطاقات والأزرار
local_css("""
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #2E7D32;
        background-color: white;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #2E7D32;
        color: white;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #1A5276;
    }
""")
