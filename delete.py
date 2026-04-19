import os
import sys
import urllib3
import json
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# From Gitlab CI/CD
PORTAINER_URL = os.getenv("PORTAINER_URL")
API_KEY = os.getenv("PORTAINER_TOKEN")
# Same logic as in deploy.py to determine stack name
STACK_NAME = f"{os.getenv('GITLAB_USER_LOGIN', 'unknown')}-{os.getenv('CI_COMMIT_REF_SLUG', 'default-stack')}"
ENDPOINT_ID = 8
# Load the compose-file
COMPOSE_FILE = "docker-compose.yml" 

if not PORTAINER_URL or not API_KEY:
    print("Error: PORTAINER_URL and PORTAINER_TOKEN environment variables must be set.")
    sys.exit(1)

if not STACK_NAME:
    print("Error: CI_COMMIT_REF_SLUG environment variable is not set.")
    sys.exit(1)

print(f"DEBUG: PORTAINER_URL = {PORTAINER_URL}")
print(f"DEBUG: STACK_NAME = {STACK_NAME}")
print(f"DEBUG: API_KEY length = {len(API_KEY) if API_KEY else 'EMPTY'}")


headers = {
    "X-API-Key": API_KEY
}

def get_endpoint_id():
    """Get the Swarm endpoint ID"""
    url = f"{PORTAINER_URL}/api/endpoints"
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        endpoints = response.json()
        
        for ep in endpoints:
            if ep.get("Name") == "local-swarm":
                print(f"DEBUG: Found endpoint {ep['Name']} with ID {ep['Id']}")
                return ep["Id"]
        
        return endpoints[0]["Id"] if endpoints else None
    except Exception as e:
        print(f"Error fetching endpoints: {e}")
        return None
    
def get_swarm_id(endpoint_id):
    url = f"{PORTAINER_URL}/api/endpoints/{endpoint_id}/docker/swarm"
    print(f"DEBUG: Fetching swarm ID from {url}")
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        swarm_data = response.json()
        swarm_id = swarm_data.get("ID")
        print(f"DEBUG: Swarm ID = {swarm_id}")
        return swarm_id
    except Exception as e:
        print(f"Error fetching swarm ID: {e}")
        return None
    

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
        print(f"Deleting from: {delete_url}")
        
        response = requests.delete(delete_url, headers=headers, verify=False)
        response.raise_for_status()
        print(f"Stack '{STACK_NAME}' deleted successfully.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    delete_stack()