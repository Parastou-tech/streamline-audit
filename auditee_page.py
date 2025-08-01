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
        modelId="anthropic.claude-v2",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"prompt": f"\n\nHuman: {prompt}\n\nAssistant:", "max_tokens_to_sample": 1000})
    )
    raw_body = response["body"].read()
    decoded_body = raw_body.decode("utf-8")

    # Parse Bedrock response robustly
    body_json = json.loads(decoded_body)
    if "completion" in body_json:
        summary = body_json["completion"]
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

        # extract text content
        extracted_text = " ".join([b["Text"] for b in blocks if b["BlockType"] == "LINE"])
        
        # Debug: Show extracted text
        st.write("**Extracted Text:**", extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
        
        # Use Claude to analyze compliance with lenient prompt
        compliance_prompt = (
            f"You are reviewing a document for audit compliance. Be very lenient.\n\n"
            f"AUDIT REQUEST: {requests[0]['doc']} - {requests[0]['desc']}\n\n"
            f"DOCUMENT CONTENT: {extracted_text[:1000]}\n\n"
            f"Does this document relate to, mention, or contain any information about the requested topic? "
            f"If there's ANY connection or relevance, respond 'COMPLIANT'. "
            f"Only respond 'NON-COMPLIANT' if completely unrelated."
        )
        
        compliance_resp = bedrock.invoke_model(
            modelId="anthropic.claude-v2",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"prompt": f"\n\nHuman: {compliance_prompt}\n\nAssistant:", "max_tokens_to_sample": 500})
        )
        
        compliance_raw = compliance_resp["body"].read().decode("utf-8")
        compliance_json = json.loads(compliance_raw)
        
        if "completion" in compliance_json:
            compliance_result = compliance_json["completion"]
        else:
            compliance_result = compliance_raw
            
        # Debug: Show AI response
        st.write("**AI Analysis:**", compliance_result)
        
        is_compliant = "COMPLIANT" in compliance_result.upper() and "NON-COMPLIANT" not in compliance_result.upper()

        if not is_compliant:
            st.error("Document marked as non-compliant")
            # Generate an example of the correct document format via Titan
            example_prompt = (
                f"Based on the audit request: {requests[0]['doc']} - {requests[0]['desc']}, "
                "provide a brief example of what a valid document should look like."
            )
            example_resp = bedrock.invoke_model(
                modelId="anthropic.claude-v2",
                contentType="application/json",
                accept="application/json",
                body=json.dumps({"prompt": f"\n\nHuman: {example_prompt}\n\nAssistant:", "max_tokens_to_sample": 500})
            )
            example_raw = example_resp["body"].read().decode("utf-8")
            example_json = json.loads(example_raw)
            if "completion" in example_json:
                example_text = example_json["completion"]
            else:
                example_text = example_raw
            st.info("Here’s what a valid document could look like:")
            st.write(example_text)
        else:
            st.success("Document is compliant with audit requirements!")