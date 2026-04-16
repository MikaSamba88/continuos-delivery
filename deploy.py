import requests
import os
import sys
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# From Gitlab CI/CD
PORTAINER_API_URL = os.getenv("PORTAINER_API_URL", "https://portainer.doe25.swarm.chas-lab.dev/api")
PORTAINER_PASSWORD = os.getenv("PORTAINER_PASSWORD")
CI_PROJECT_NAMESPACE_SLUG = os.getenv("CI_PROJECT_NAMESPACE_SLUG", "default")
CI_PROJECT_NAME = os.getenv("CI_PROJECT_NAME", "project")
CI_COMMIT_REF_SLUG = os.getenv("CI_COMMIT_REF_SLUG", "main")
CI_COMMIT_REF_NAME = os.getenv("CI_COMMIT_REF_NAME", "main")
CI_DEFAULT_BRANCH = os.getenv("CI_DEFAULT_BRANCH", "main")

STACK_NAME = f"{CI_PROJECT_NAMESPACE_SLUG}-{CI_PROJECT_NAME}-{CI_COMMIT_REF_SLUG}"
COMPOSE_FILE = "docker-compose.yaml"
DEPLOYABLE_COMPOSE_FILE = "deployable-compose.yaml"

if not PORTAINER_PASSWORD:
    print("Error: PORTAINER_PASSWORD environment variable must be set.")
    sys.exit(1)

print(f"About to create a stack named: {STACK_NAME}")

def get_portainer_token():
    """Authenticate with Portainer and get JWT token"""
    url = f"{PORTAINER_API_URL}/auth"
    payload = {
        "Username": "gg",
        "Password": PORTAINER_PASSWORD
    }
    try:
        response = requests.post(url, json=payload, verify=False)
        response.raise_for_status()
        token = response.json().get("jwt")
        if not token:
            print("Error: No JWT token received from Portainer")
            sys.exit(1)
        return token
    except Exception as e:
        print(f"Error authenticating with Portainer: {e}")
        sys.exit(1)

def get_endpoint_info(token):
    """Finding ID for Environment"""
    url = f"{PORTAINER_API_URL}/endpoints"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        endpoints = response.json()

        for ep in endpoints:
            if ep["Name"] == "local-swarm":
                endpoint_id = ep["Id"]
                print(f"Targeting endpoint with Id {endpoint_id}")
                return endpoint_id, None
            
        if endpoints:
            endpoint_id = endpoints[0]["Id"]
            print(f"Targeting endpoint with Id {endpoint_id}")
            return endpoint_id, None
        return None, None
    except Exception as e:
        print(f"Error fetching endpoints: {e}")
        sys.exit(1)

def get_swarm_id(token, endpoint_id):
    """Get swarm cluster ID"""
    url = f"{PORTAINER_API_URL}/endpoints/{endpoint_id}/docker/swarm"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        swarm_id = response.json().get("ID")
        if not swarm_id:
            print("Error: No swarm ID found")
            sys.exit(1)
        print(f"Targeting swarm cluster with ID {swarm_id}")
        return swarm_id
    except Exception as e:
        print(f"Error fetching swarm info: {e}")
        sys.exit(1)

def get_image_tag():
    """Determine image tag based on branch"""
    if CI_COMMIT_REF_NAME == CI_DEFAULT_BRANCH:
        return "latest"
    return CI_COMMIT_REF_NAME

def create_deployable_compose():
    """Substitute environment variables in compose file"""
    try:
        with open(COMPOSE_FILE, 'r') as f:
            content = f.read()
        
        # Substitute environment variables
        for key, value in os.environ.items():
            content = content.replace(f"${{{key}}}", str(value))
            content = content.replace(f"${key}", str(value))
        
        with open(DEPLOYABLE_COMPOSE_FILE, 'w') as f:
            f.write(content)
        
        print(f"Created {DEPLOYABLE_COMPOSE_FILE}")
        print("Content:")
        print(content)
    except FileNotFoundError:
        print(f"Error: {COMPOSE_FILE} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error creating deployable compose file: {e}")
        sys.exit(1)

def get_stack_id(token, endpoint_id):
    """Get existing stack ID if it exists"""
    url = f"{PORTAINER_API_URL}/stacks"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        stacks = response.json()
        
        for stack in stacks:
            if stack["Name"] == STACK_NAME and stack.get("EndpointId") == endpoint_id:
                return stack["Id"]
        
        return None
    except Exception as e:
        print(f"Error fetching stacks: {e}")
        sys.exit(1)

def deploy_stack(token, endpoint_id, swarm_id, stack_id):
    """Create or update stack to Portainer"""
    if stack_id is None:
        # Create new stack
        print(f"Creating a new stack {STACK_NAME}")
        url = f"{PORTAINER_API_URL}/stacks/create/swarm/file?endpointId={endpoint_id}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            with open(DEPLOYABLE_COMPOSE_FILE, 'rb') as f:
                files = {"file": f}
                data = {
                    "Name": STACK_NAME,
                    "SwarmID": swarm_id
                }
                r = requests.post(url, headers=headers, files=files, data=data, verify=False)
                r.raise_for_status()
                print("Stack created successfully.")
                print(json.dumps(r.json(), indent=2))
        except Exception as e:
            print(f"Error creating stack: {e}")
            sys.exit(1)
    else:
        # Update existing stack
        print(f"Re-deploying stack with ID {stack_id}")
        url = f"{PORTAINER_API_URL}/stacks/{stack_id}?endpointId={endpoint_id}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            with open(DEPLOYABLE_COMPOSE_FILE, 'r') as f:
                compose_content = f.read()
            
            payload = {
                "prune": True,
                "RepullImageAndRedeploy": True,
                "stackFileContent": compose_content
            }
            
            r = requests.put(url, headers=headers, json=payload, verify=False)
            r.raise_for_status()
            print("Stack updated successfully.")
            print(json.dumps(r.json(), indent=2))
        except Exception as e:
            print(f"Error updating stack: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Get authentication token
    token = get_portainer_token()
    
    # Get endpoint and swarm IDs
    eid, _ = get_endpoint_info(token)
    if not eid:
        print("No endpoints found in Portainer.")
        sys.exit(1)
    
    swarm_id = get_swarm_id(token, eid)
    
    # Get image tag
    image_tag = get_image_tag()
    os.environ["IMAGE_TAG"] = image_tag
    
    # Create deployable compose file
    create_deployable_compose()
    
    # Get existing stack ID
    stack_id = get_stack_id(token, eid)
    
    # Deploy stack
    deploy_stack(token, eid, swarm_id, stack_id)
    
    print("\nDeployment completed successfully!")