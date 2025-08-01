# Audit Agent Demo (Streamlit + AWS)

A minimal, serverless proof-of-concept that streamlines a university audit workflow. Auditors can issue requests for specific documents; auditees see a plain-English summary with examples, upload files, and get instant compliance feedback via AWS Textract and Bedrock/Titan Text.

⸻

### Features
	•	Auditor Dashboard
	•	Submit a document name & description
	•	Automatically store the latest request in S3
	•	Auditee Dashboard
	•	Fetch and display the current audit request
	•	Summarize requests with Amazon Titan Text
	•	Upload PDF or image for OCR via Textract
	•	Poll asynchronously for multi-page PDFs or synchronously for images
	•	Print raw OCR lines and compliance results to the terminal
	•	Show a friendly error or success message in the UI
	•	Generate examples of correct document formats when non-compliant

⸻

### Architecture
	1.	Streamlit Front End
	•	Two pages: auditor_page.py and auditee_page.py
	2.	AWS S3
	•	Bucket audit-12-test for request JSON and uploaded documents
	3.	AWS Textract
	•	detect_document_text for images
	•	start_document_text_detection + polling for PDFs
	4.	AWS Bedrock / Titan Text
	•	Summarize requests via managed Titan Text models
	•	Generate corrective examples when needed

⸻

### Prerequisites
	•	AWS account with permissions for S3, Textract, and Bedrock
	•	AWS CLI v2 installed & configured
	•	Python 3.9+
	•	pip (and optionally venv or pipenv for virtual environments)
	•	Streamlit, boto3, python-dotenv installed

⸻

### AWS Console Setup
	1.	Create an S3 bucket
	•	Name: audit-12-test (or configure your own via BUCKET_NAME)
	•	Region: us-west-2
	2.	Create an IAM role or user with policies:
	•	AmazonS3FullAccess (or a least-privilege policy for your bucket)
	•	AmazonTextractFullAccess
	•	AmazonBedrockFullAccess
	3.	(Optional) SNS topic & Lambda for async callbacks if you prefer event-driven processing over polling

⸻

Local Setup

#### Clone the repository
git clone https://github.com/your-org/audit-agent.git
cd audit-agent

#### Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

#### Install dependencies
pip install -r requirements.txt

#### Configure AWS credentials
aws configure           # or aws configure sso
export AWS_DEFAULT_REGION=us-west-2
##### Optionally create a .env file with:
##### AWS_ACCESS_KEY_ID=...
##### AWS_SECRET_ACCESS_KEY=...
##### AWS_DEFAULT_REGION=us-west-2
##### BUCKET_NAME=audit-12-test


⸻

### Running the App

streamlit run app.py

	•	Open your browser at http://localhost:8501
	•	Log in as “Auditor” or “Auditee” (stub authentication)
	•	Navigate to the appropriate dashboard

⸻

### Folder Structure

.
├── app.py                # Main router for auditor/auditee views
├── auditor_page.py       # Auditor Dashboard UI & S3 request logic
├── auditee_page.py       # Auditee Dashboard UI, Textract & Titan logic
├── create_bucket.py      # Optional script to create S3 bucket
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (AWS keys, BUCKET_NAME)


⸻

### Usage
	1.	Auditor
	•	Enter “Document name” and “Description”
	•	Click “Send request” → request stored in S3
	2.	Auditee
	•	View the plain-English summary + examples
	•	Upload a PDF or image
	•	Terminal prints raw OCR lines & compliance dict
	•	UI shows success or a generated corrective example

⸻

### Contributing
	1.	Fork the repository
	2.	Create a feature branch
	3.	Commit your changes and open a pull request

⸻

License

This project is licensed under the MIT License.