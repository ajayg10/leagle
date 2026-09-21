from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os
import sys

# Load from .env if possible
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    print("❌ NVIDIA_API_KEY NOT FOUND")
    sys.exit(1)

try:
    client = ChatNVIDIA(api_key=api_key)
    models = client.available_models
    print("\n=== AVAILABLE NVIDIA MODELS ===")
    for m in models:
        print(f"- {m.id}")
except Exception as e:
    print(f"❌ Error: {e}")
