import requests
import os
import sys
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# From Gitlab CI/CD
PORTAINER_URL = os.getenv("PORTAINER_URL")
PORTAINER_TOKEN = os.getenv("PORTAINER_PASSWORD")
STACK_NAME = os.getenv("CI_COMMIT_REF_SLUG", "default-stack") # Using branch name as stack name 
# Load the compose-file
COMPOSE_FILE = "docker-compose.yml" 


if not PORTAINER_URL or not PORTAINER_TOKEN:
    print("Error: PORTAINER_URL and PORTAINER_API_TOKEN environment variables must be set.")
    sys.exit(1)

headers = {
    "X-API-Key": PORTAINER_TOKEN
}

def get_endpoint_id():
    """Finding ID for Environment"""
    url = f"{PORTAINER_URL}/api/endpoints"
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        endpoints = response.json()
        for ep in endpoints:
            if ep["Name"] == "local":
                return ep["Id"]
            
        # If Endpoint not found, take first available
        return endpoints[0]["Id"] if endpoints else None
    except Exception as e:
        print(f"Error fetching endpoints: {e}")
        sys.exit(1)

def deploy_stack(endpoint_id):
# Deploying stack to Portainer
    with open(COMPOSE_FILE, 'r') as f:
        compose_content = f.read()
    stack_url = f"{PORTAINER_URL}/api/stacks"
    params = {"filters": json.dumps({"Name": [STACK_NAME]})}
    r_list = requests.get(stack_url, headers=headers, params=params, verify=False)
    existing_stacks = r_list.json()

    if existing_stacks:
        stack_id = existing_stacks[0]["Id"]
        print(f"Updating existing stack '{STACK_NAME}' (ID: {stack_id})")
        url = f"{PORTAINER_URL}/api/stacks/{stack_id}?endpointId={endpoint_id}"
        payload = {
            "StackFileContent": compose_content,
            "prune": True
        }
        r = requests.put(url, headers=headers, json=payload, verify=False)
    else:
        print(f"Creating new stack '{STACK_NAME}'")
        url = f"{PORTAINER_URL}/api/stacks/create/swarm/file?endpointId={endpoint_id}"
        payload = {
            "Name": STACK_NAME,
            "StackFileContent": compose_content,
            "Prune": True
        }
        print(url)
        r = requests.post(url, headers=headers, json=payload, verify=False)
    if r.status_code in [200, 204]:
        print(f"Stack '{STACK_NAME}' deployed successfully.")
    else:
        print(f"Failed to deploy stack '{STACK_NAME}'. Status code: {r.status_code}, Response: {r.text}")
        sys.exit(1)

if __name__ == "__main__":
    eid = get_endpoint_id()
    if eid:
        deploy_stack(eid)
        print(f"Deploying to Portainer Endpoint ID: {eid}")
    else:
        print("No endpoints found in Portainer.")
        sys.exit(1)