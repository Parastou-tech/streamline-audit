# auditee_page.py

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

def auditee_page():
    st.title("Auditee Dashboard")
    
    # Logout button
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # load audit requests
    try:
        resp = s3.get_object(Bucket=BUCKET, Key="audit_requests.json")
        requests = json.loads(resp["Body"].read())
    except s3.exceptions.NoSuchKey:
        st.warning("No audit requests found.")
        st.stop()

    st.subheader("Requested Documents")
    for r in requests:
        st.markdown(f"**{r['doc']}**: {r['desc']}")

    # summarize requests
    prompt = (
        "Summarize these audit requests in plain English for a non-expert "
        "and give an example for each:\n\n"
        + "\n".join(f"- {r['doc']}: {r['desc']}" for r in requests)
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

    st.subheader("Summarized Requests & Examples")
    st.write(summary)

    # upload and OCR check
    st.subheader("Upload Document for Compliance Check")
    uploaded_file = st.file_uploader("Choose document to upload", type=["pdf", "png", "jpg"])
    if uploaded_file:
        filename = uploaded_file.name
        content = uploaded_file.read()
        s3.put_object(Bucket=BUCKET, Key=filename, Body=content)

        ext = filename.rsplit(".", 1)[-1].lower()
        if ext == "pdf":
            start_resp = textract.start_document_text_detection(
                DocumentLocation={"S3Object": {"Bucket": BUCKET, "Name": filename}}
            )
            job_id = start_resp["JobId"]
            while True:
                job_resp = textract.get_document_text_detection(JobId=job_id)
                status = job_resp["JobStatus"]
                if status == "SUCCEEDED":
                    blocks = job_resp["Blocks"]
                    break
                elif status == "FAILED":
                    raise RuntimeError(f"Textract job {job_id} failed")
                time.sleep(1)
        else:
            sync_resp = textract.detect_document_text(
                Document={"S3Object": {"Bucket": BUCKET, "Name": filename}}
            )
            blocks = sync_resp["Blocks"]

        # extract lines and compliance
        lines = [b["Text"] for b in blocks if b["BlockType"] == "LINE"]
        compliance = {}
        for r in requests:
            keyword = r["doc"].split()[0].lower()
            compliance[r["doc"]] = any(keyword in line.lower() for line in lines)

        if not all(compliance.values()):
            missing = [doc for doc, ok in compliance.items() if not ok]
            correction_prompt = (
                f"You are a compliance assistant. You received the wrong document. "
                f"OCR detected: {', '.join(lines[:5])}... We were looking for {', '.join(missing)}. "
                "Generate a message explaining the mismatch and an example of the correct document format."
            )
            corr_resp = bedrock.invoke_model(
                modelId="amazon.titan-text-lite-v1",
                contentType="application/json",
                accept="application/json",
                body=json.dumps({"inputText": correction_prompt})
            )
            raw = corr_resp["body"].read().decode("utf-8")
            body_json = json.loads(raw)
            if "outputText" in body_json:
                message = body_json["outputText"]
            elif "results" in body_json and body_json["results"]:
                result0 = body_json["results"][0]
                message = (
                    result0.get("outputText")
                    or result0.get("output")
                    or result0.get("generatedText")
                    or raw
                )
            else:
                message = raw
            st.error(message)
        else:
            st.success("All requested documents are compliant!")