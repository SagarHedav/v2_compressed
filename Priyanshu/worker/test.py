# test_pinecone.py
import os
from dotenv import load_dotenv

load_dotenv()

print("Current PINECONE_ENVIRONMENT:", os.getenv("PINECONE_ENVIRONMENT"))

# Check Pinecone console regions
print("\nCommon Pinecone regions:")
print("1. us-east-1 (North Virginia)")
print("2. us-west-2 (Oregon)")
print("3. eu-west-1 (Ireland)")
print("4. ap-southeast-1 (Singapore)")