import requests
import os
import sys
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# From Gitlab CI/CD
PORTAINER_URL = os.getenv("PORTAINER_URL")
PORTAINER_TOKEN = os.getenv("PORTAINER_TOKEN")
STACK_NAME = os.getenv("CI_COMMIT_REF_SLUG", "default-stack") # Using branch name as stack name 
# Load the compose-file
COMPOSE_FILE = "docker-compose.yml" 


if not PORTAINER_URL or not PORTAINER_TOKEN:
    print("Error: PORTAINER_URL and PORTAINER_TOKEN environment variables must be set.")
    sys.exit(1)

headers = {
    "X-API-Key": PORTAINER_TOKEN,
    "Content-Type": "application/json"
}

def get_endpoint_info():
    """Finding ID for Environment"""
    url = f"{PORTAINER_URL}/api/endpoints"
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        endpoints = response.json()

        for ep in endpoints:
            if ep["Name"] == "local-swarm":
                return ep["Id"], None
            
        if endpoints:
            return endpoints[0]["Id"], None
        return None, None
    except Exception as e:
        print(f"Error fetching endpoints: {e}")
        sys.exit(1)


def deploy_stack(endpoint_id):
# Deploying stack to Portainer
    try:
        with open(COMPOSE_FILE, 'r') as f:
            compose_content = f.read()
    except FileNotFoundError:
        print(f"Error: {COMPOSE_FILE} not found.")
        sys.exit(1)

    stack_url = f"{PORTAINER_URL}/api/stacks"
    try:
        r_list = requests.get(stack_url, headers=headers, verify=False)
        r_list.raise_for_status()
        existing_stacks = [s for s in r_list.json() if s["Name"] == STACK_NAME]
    except Exception as e:
        print(f"Error fetching stacks: {e}")
        sys.exit(1)

    if existing_stacks:
        stack_id = existing_stacks[0]["Id"]
        print(f"Updating existing stack '{STACK_NAME}' (ID: {stack_id})")
        url = f"{PORTAINER_URL}/api/stacks/{stack_id}?endpointId={endpoint_id}"
        payload = {
            "StackFileContent": compose_content,
            "prune": True,
            "pullImage": True
        }
        r = requests.put(url, headers=headers, json=payload, verify=False)
    else:
        print(f"Creating new stack '{STACK_NAME}'")
        url = f"{PORTAINER_URL}/api/stacks/create/swarm?endpointId={endpoint_id}"
        payload = {
            "name": STACK_NAME,
            "stackFileContent": compose_content,
        }
        r = requests.post(url, headers=headers, json=payload, verify=False)

    if r.status_code in [200, 201, 204]:
        print(f"Stack '{STACK_NAME}' deployed successfully.")
    else:
        print(f"Failed to deploy stack '{STACK_NAME}'. Status code: {r.status_code}")
        print(f"Response: {r.text}")
        sys.exit(1)

if __name__ == "__main__":
    eid, _ = get_endpoint_info()
    if eid:
        deploy_stack(eid, sid)
        print(f"Deploying to Portainer Endpoint ID: {eid}")
    else:
        print("No endpoints found in Portainer.")
        sys.exit(1)