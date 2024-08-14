import os
import pinecone
from pinecone import Pinecone

# Pinecone API
pc_api_key = os.getenv("PINECONE_API_KEY")
pc_client = Pinecone(api_key=pc_api_key)