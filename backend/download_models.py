"""Pre-download models during build time to speed up startup."""
import os
print("Downloading embedding model...")

from sentence_transformers import SentenceTransformer

# Download the model during build
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ Model downloaded successfully!")

embedding = model.encode("test")
print(f"✓ Model loaded, embedding size: {len(embedding)}")