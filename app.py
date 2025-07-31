import os
from dotenv import load_dotenv
import streamlit as st
import boto3
import json
from auditor_page import auditor_page
from auditee_page import auditee_page

load_dotenv()
region = os.getenv("AWS_DEFAULT_REGION", "us-west-2")

# AWS clients
s3       = boto3.client("s3",       region_name=region)
textract = boto3.client("textract", region_name=region)
bedrock  = boto3.client("bedrock-runtime", region_name=region)

# Your bucket name
BUCKET = os.getenv("BUCKET_NAME", "audit-12-test")

def main():
    # Login page
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.title("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["Auditor", "Auditee"])
            login_clicked = st.form_submit_button("Log In")
        if login_clicked:
            # Stub for authentication logic
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['role'] = role
            st.rerun()
        return

    # After successful login, route to the appropriate page
    if st.session_state['role'] == "Auditor":
        auditor_page()
    else:
        auditee_page()

if __name__ == "__main__":
    main()