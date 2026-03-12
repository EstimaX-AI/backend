import os
import boto3
import requests
from dotenv import load_dotenv

load_dotenv(".env.dev")

S3_ENDPOINT = os.getenv("SUPABASE_S3_ENDPOINT")
ACCESS_KEY = os.getenv("SUPABASE_ACCESS_KEY")
SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)


def upload_pdf(file_bytes: bytes, filename: str):

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=filename,
        Body=file_bytes,
        ContentType="application/pdf"
    )

    return create_signed_url(filename)


def create_signed_url(filename):

    url = f"{SUPABASE_URL}/storage/v1/object/sign/{BUCKET_NAME}/{filename}"

    headers = {
        "Authorization": f"Bearer {SERVICE_ROLE}",
        "Content-Type": "application/json"
    }

    data = {
        "expiresIn": 3600
    }

    res = requests.post(url, json=data, headers=headers)

    if res.status_code != 200:
        raise Exception(f"Supabase signed URL request failed: {res.text}")

    response_data = res.json()

    if "signedURL" not in response_data:
        raise Exception(f"Supabase signed URL generation failed: {response_data}")

    signed_path = response_data["signedURL"]

    return f"{SUPABASE_URL}/storage/v1{signed_path}"
