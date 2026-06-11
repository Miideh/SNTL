import requests
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv
load_dotenv()

cred = DefaultAzureCredential()
endpoint = os.getenv('AZURE_PROJECT_ENDPOINT')

scopes = [
    'https://management.azure.com/.default',
    'https://ml.azure.com/.default',
    'https://cognitiveservices.azure.com/.default'
]

versions = ['2024-05-01-preview', '2025-03-01-preview']

for scope in scopes:
    token = cred.get_token(scope)
    headers = {
        'Authorization': f'Bearer {token.token}',
        'Content-Type': 'application/json'
    }
    for v in versions:
        r = requests.post(f'{endpoint}/threads?api-version={v}', headers=headers, json={})
        short_scope = scope.split('/')[2]
        print(f'{short_scope} | {v}: {r.status_code} {r.text[:80]}')
