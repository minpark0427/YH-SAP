import streamlit as st
import json
from auto_sap.classes.protocol_classes import Protocol
from auto_sap.generate_templates.generate_simple_template import get_autocode_conversation_for_protocol

st.set_page_config(page_title="SAP Auto-Code Assistant", layout="wide")

st.title("🧠 SAP Auto-Code Assistant")
st.markdown("Upload a protocol, auto-generate SAP content, extract autocode JSON, and correct it via chat.")

# --- SESSION STATE ---
if "convo" not in st.session_state:
    st.session_state.convo = None

if "result" not in st.session_state:
    st.session_state.result = None

# --- FILE UPLOAD ---
uploaded = st.file_uploader("Upload protocol (.txt or .pdf)", type=["txt", "pdf"])

if uploaded:
    st.success(f"File uploaded: {uploaded.name}")

    # Read the protocol text
    protocol = Protocol(uploaded)
    protocol_text = protocol.protocol_txt

    st.subheader("📄 Protocol preview (first 1,000 chars)")
    st.text(protocol_text[:1000] + " ...")


# --- RUN EXTRACTION ---
if uploaded and st.button("🚀 Run SAP Generation + Autocode Extraction"):

    with st.spinner("Running extraction..."):
        convo = get_autocode_conversation_for_protocol(
            protocol_txt=protocol_text,
            model="gpt-5-nano",
            validate=False
        )

        st.session_state.convo = convo
        st.session_state.result = convo.result

    st.success("Extraction complete!")

# --- DISPLAY RESULTS ---
if st.session_state.result:

    st.header("📌 Extracted Autocode JSON")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Timepoints")
        st.json(st.session_state.result.get("timepoints", []))

    with col2:
        st.subheader("Variables")
        st.json(st.session_state.result.get("variables", []))

    with col3:
        st.subheader("Analyses")
        st.json(st.session_state.result.get("analyses", []))

    st.divider()


# --- CHAT CORRECTION UI ---
if st.session_state.convo:

    st.header("💬 Human-in-the-loop: Fix mistakes via chat")

    user_msg = st.text_area("Your instruction:", placeholder="e.g., Remove the 6-month timepoint.")
    submit_chat = st.button("Apply Change")

    if submit_chat and user_msg.strip():

        with st.spinner("Updating JSON using LLM..."):
            new_json = st.session_state.convo.chat(user_msg)
            st.session_state.result = new_json

        st.success("Updated JSON")

        st.subheader("Updated Timepoints")
        st.json(new_json.get("timepoints", []))

        st.subheader("Updated Variables")
        st.json(new_json.get("variables", []))

        st.subheader("Updated Analyses")
        st.json(new_json.get("analyses", []))

        st.divider()

# --- DOWNLOAD FINAL JSON ---
if st.session_state.result:
    st.download_button(
        label="⬇️ Download Final Autocode JSON",
        data=json.dumps(st.session_state.result, indent=2),
        file_name="autocode_result.json",
        mime="application/json"
    )
