import os
from dotenv import load_dotenv

load_dotenv()

print("ACCESS KEY:", os.getenv("SUPABASE_ACCESS_KEY_ID"))
print("SECRET KEY:", os.getenv("SUPABASE_SECRET_ACCESS_KEY"))
print("ENDPOINT:", os.getenv("SUPABASE_S3_ENDPOINT"))