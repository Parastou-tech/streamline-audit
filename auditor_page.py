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
    st.title("Auditor Dashboard")
    
    # Logout button
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()
    with st.form("auditor_form"):
        doc_name = st.text_input("Document name", placeholder="e.g. Coaching Certification")
        doc_desc = st.text_area("Description of the document", placeholder="Describe what you need")
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

        # Generate plain-English summary & example via Titan
        prompt = (
            "Summarize this audit request for a non-expert and give one concrete example:\n"
            f"Document: {doc_name}\nDescription: {doc_desc}"
        )
        response = bedrock.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": prompt})
        )
        raw_body = response["body"].read()
        decoded_body = raw_body.decode("utf-8")

        # Parse Bedrock response robustly
        body_json = json.loads(decoded_body)
        if "outputText" in body_json:
            summary = body_json["outputText"]
        elif "results" in body_json and body_json["results"]:
            result0 = body_json["results"][0]
            summary = (
                result0.get("outputText")
                or result0.get("output")
                or result0.get("generatedText")
                or decoded_body
            )
        else:
            summary = decoded_body

        new_request["summary"] = summary
        requests = [new_request]

        st.subheader("Generated Summary & Example")
        st.write(summary)

        # save back to S3
        s3.put_object(
            Bucket=BUCKET,
            Key="audit_requests.json",
            Body=json.dumps(requests)
        )
        st.success("Recipient notified of your request.")