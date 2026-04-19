import requests
import os
import sys
import urllib3
import json
from deploy import get_endpoint_id

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PORTAINER_URL = os.getenv("PORTAINER_URL")
API_KEY = os.getenv("PORTAINER_TOKEN")
STACK_NAME = f"samba-{os.getenv('CI_PROJECT_NAME')}-{os.getenv('CI_COMMIT_REF_SLUG')}"

headers = {
    "X-API-Key": API_KEY
}

# Find the stack by name and delete it using the Portainer API
def delete_stack():
    endpoint_id = get_endpoint_id()
    if not endpoint_id:
        print("Could not find endpoint")
        sys.exit(1)
    
    stack_url = f"{PORTAINER_URL}/api/stacks"
    params = {"filters": json.dumps({"Name": [STACK_NAME]})}
    
    try:
        print(f"DEBUG: Fetching stacks from {stack_url}")
        r = requests.get(stack_url, headers=headers, verify=False)
        r.raise_for_status()
        all_stacks = r.json()
        
        print(f"DEBUG: All stacks: {[s.get('Name') for s in all_stacks]}")
        print(f"DEBUG: Looking for: {STACK_NAME}")
        
        stack = next((s for s in all_stacks if s.get('Name') == STACK_NAME), None)
        
        if not stack:
            print(f"Stack '{STACK_NAME}' not found.")
            return
        
        delete_url = f"{PORTAINER_URL}/api/stacks/{stack['Id']}?endpointId={endpoint_id}"
        params = {"endpointId": endpoint_id}
        print(f"Trying to delete stack with URL: {delete_url} and params: {params}")
        
        response = requests.delete(delete_url, headers=headers, verify=False)
        response.raise_for_status()
        print(f"Stack '{STACK_NAME}' deleted successfully.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    delete_stack()