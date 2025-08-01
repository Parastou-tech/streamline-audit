# auditor_page.py

import os
import json
import time
import streamlit as st
import boto3
from dotenv import load_dotenv

load_dotenv()
region = os.getenv("AWS_DEFAULT_REGION", "us-west-2")

# AWS clients
s3       = boto3.client("s3",       region_name=region)
textract = boto3.client("textract", region_name=region)
bedrock  = boto3.client("bedrock-runtime", region_name=region)

# Your bucket name
BUCKET = os.getenv("BUCKET_NAME", "audit-12-test")

def auditor_page():
    col1, col2 = st.columns([10, 1.3])
    with col1:
        st.title("Auditor Dashboard")
    with col2:
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
    with st.form("auditor_form"):
        doc_name = st.text_input("Document name", placeholder="e.g. Coaching Certification")
        doc_desc = st.text_area("Description of the document", placeholder="Describe what you need")
        col1, col2, col3 = st.columns([2.2, 2, 1])
    with col3:
        submitted = st.form_submit_button("Send request")

    if submitted:
        # load existing requests from S3 or start fresh
        try:
            resp = s3.get_object(Bucket=BUCKET, Key="audit_requests.json")
            requests = json.loads(resp["Body"].read())
        except s3.exceptions.NoSuchKey:
            requests = []

        # override requests to only include the current request with summary
        new_request = {"doc": doc_name, "desc": doc_desc}

        requests = [new_request]

        # save back to S3
        s3.put_object(
            Bucket=BUCKET,
            Key="audit_requests.json",
            Body=json.dumps(requests)
        )
        st.success("Recipient notified of your request.")