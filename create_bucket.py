import boto3
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client("s3")
bucket_name = "audit-12-test"

try:
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )
    print(f"Bucket {bucket_name} created successfully")
except Exception as e:
    print(f"Error: {e}")