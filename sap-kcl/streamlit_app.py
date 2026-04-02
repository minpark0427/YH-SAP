import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="SAPAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

logo_path = Path(__file__).parent / "sapai_logo.png"
if logo_path.exists():
    st.html(f'''
        <div style="text-align:center;padding:1rem 0 0;">
            <img src="data:image/png;base64,{__import__("base64").b64encode(logo_path.read_bytes()).decode()}" style="height:60px;">
        </div>
    ''')

html_path = Path(__file__).parent / "landing.html"
html = html_path.read_text()

parts = html.split('<p class="sl-hero-sub">')

st.html(parts[0])

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Draft Your SAP", type="primary", use_container_width=True):
        st.login()

st.html('<p class="sl-hero-sub">' + parts[1])
