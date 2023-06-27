import os
import requests
import re


# script params
API_HOST = 'https://api.sandbox-m2.ll9k.p1.openshiftapps.com:6443'
NAMESPACE = os.environ['NAMESPACE']
AUTH_TOKEN = os.environ['AUTH_TOKEN']
DELETED_RESOURCES_TYPES = ['route', 'service']

# set resources to be deleted
resources_by_url = {
    'service': f'{API_HOST}/api/v1/namespaces/{NAMESPACE}/services',
    'route': f'{API_HOST}/apis/route.openshift.io/v1/namespaces/{NAMESPACE}/routes',
    'pod': f'{API_HOST}/api/v1/namespaces/{NAMESPACE}/pods',
}
resources_by_pattern = {
    'pod': '^python-basic-([0-9]+?)-b[a-z]*$',
    'route': '^route([0-9]+?)$',
    'service': '^service-([0-9]+?)$'
}

# set header for delete request
headers = {
    'Authorization': f'Bearer {AUTH_TOKEN}'
}

# fetch all relevant pods with their status
pods_ids = []
response = requests.get(resources_by_url['pod'], headers=headers, verify=False)
if response.status_code != 200:
    raise Exception(f'could not reach server: {response.json()}')
for item in response.json()['items']:
    pod_name = item['metadata']['name']
    # verify it's relevant pod (by name)
    match = re.search(resources_by_pattern['pod'], pod_name)
    if match is not None:
        pods_ids.append(int(match.group(1)))

# fetch every resource type and delete its relevant objects
for resource in DELETED_RESOURCES_TYPES:
    received_resource = requests.get(resources_by_url[resource], headers=headers, verify=False)
    for item in received_resource.json()['items']:
        resource_name = item['metadata']['name']
        resource_match = re.search(resources_by_pattern[resource], resource_name)
        if resource_match is not None and int(resource_match.group(1)) in pods_ids:
            print(f"deleting {resource_name}")
            requests.delete(f'{resources_by_url[resource]}/{resource_name}', headers=headers, verify=False)
