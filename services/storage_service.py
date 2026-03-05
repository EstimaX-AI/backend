import os
import boto3
from dotenv import load_dotenv

load_dotenv()

S3_ENDPOINT = os.getenv("SUPABASE_S3_ENDPOINT")
ACCESS_KEY = os.getenv("SUPABASE_ACCESS_KEY")
SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)


class StorageService:

    @staticmethod
    def upload_pdf(file_bytes: bytes, filename: str):

        # upload file
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=file_bytes,
            ContentType="application/pdf"
        )

        # generate signed URL (30 min TTL)
        signed_url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": filename
            },
            ExpiresIn=1800
        )

        return signed_url