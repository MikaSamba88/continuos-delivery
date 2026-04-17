import requests
import os
import sys

# Config variables from Gitlab
PORTAINER_URL = os.getenv("PORTAINER_URL")
API_TOKEN = os.getenv("PORTAINER_TOKEN")
ENDPOINT_ID = 8
STACK_NAME = os.getenv("CI_ENVIROMENT_SLUG", "default-stack")
COMPOSE_FILE = "docker-compose.yml"

headers = {
    "X-API-Key": API_TOKEN
}

def deploy():
    with open(COMPOSE_FILE, 'r') as f:
        compose_content = f.read()

    response = requests.get(f"{PORTAINER_URL}/api/stacks", headers=headers)
    stacks = response.json()
    existing_stack = next((s for s in stacks if s['Name'] == STACK_NAME), None)

    if existing_stack:
        # Uppdatera befintlig stack
        stack_id = existing_stack['Id']
        print(f"Uppdaterar stack: {STACK_NAME} (ID: {stack_id})")
        url = f"{PORTAINER_URL}/api/stacks/{stack_id}?endpointId={ENDPOINT_ID}"
        payload = {"StackFileContent": compose_content, "Prune": True}
        r = requests.put(url, headers=headers, json=payload)
    else:
        # Skapa ny stack
        print(f"Skapar ny stack: {STACK_NAME}")
        url = f"{PORTAINER_URL}/api/stacks?method=string&type=2&endpointId={ENDPOINT_ID}"
        payload = {"Name": STACK_NAME, "StackFileContent": compose_content}
        r = requests.post(url, headers=headers, json=payload)
    
    if r.status_code not in [200, 201]:
        print(f"Error: {r.text}")
        sys.exit(1)
    print("Success!")

if __name__ == "__main__":
    deploy()