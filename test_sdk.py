from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.DEBUG)
load_dotenv()

client = AgentsClient(
    endpoint=os.getenv('AZURE_PROJECT_ENDPOINT'),
    credential=DefaultAzureCredential()
)
thread = client.threads.create()
print('Thread ID:', thread.id)
