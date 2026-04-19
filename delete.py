import os
import sys
import urllib3
import json
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# From Gitlab CI/CD
PORTAINER_URL = os.getenv("PORTAINER_URL")
PORTAINER_TOKEN = os.getenv("PORTAINER_TOKEN")
# Same logic as in deploy.py to determine stack name
STACK_NAME = f"{os.getenv('GITLAB_USER_LOGIN', 'unknown')}-{os.getenv('CI_COMMIT_REF_SLUG', 'default-stack')}"

if not PORTAINER_URL or not PORTAINER_TOKEN:
    print("Error: PORTAINER_URL and PORTAINER_TOKEN environment variables must be set.")
    sys.exit(1)

if not STACK_NAME:
    print("Error: CI_COMMIT_REF_SLUG environment variable is not set.")
    sys.exit(1)

headers = {
    "X-API-Key": PORTAINER_TOKEN
}

# Find the stack by name and delete it using the Portainer API
def delete_stack():
    # Get the list of stacks to find the ID of the stack to delete
    stack_url = f"{PORTAINER_URL}/api/stacks"
    params = {
        "filters": json.dumps({"Name": [STACK_NAME]})
    }

    try:
        r = requests.get(stack_url, headers=headers, params=params, verify=False)
        r.raise_for_status()
        stacks = r.json()

        if not stacks:
            print(f"Stack '{STACK_NAME}' not found.")
            return
        
        stack_id = stacks[0]['Id']
        # need to get the endpoint ID as well
        endpoint_id = stacks[0]['EndpointId']

        # Delete the stack
        delete_url = f"{PORTAINER_URL}/api/stacks/{stack_id}?endpointId={endpoint_id}"
        print(f"Deleting stack '{STACK_NAME}' with ID {stack_id}...")

        response = requests.delete(delete_url, headers=headers, verify=False)
        response.raise_for_status()
        print(f"Stack '{STACK_NAME}' deleted successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error deleting stack: {e}")
        sys.exit(1)

if __name__ == "__main__":
    delete_stack()