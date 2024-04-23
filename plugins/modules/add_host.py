import os
import sys
import json
from http import HTTPStatus

from ansible_collections.community.privx.plugins.module_utils.privx_utils import PrivXAnsibleModule, define_argument_spec, diff_dicts
from ansible_collections.community.privx.plugins.module_utils.host_store import PrivXHostStore
from ansible_collections.community.privx.plugins.module_utils.role_store import PrivXRoleStore
from ansible_collections.community.privx.plugins.module_utils.authorizer import PrivXAuthorizer
from ansible.module_utils.basic import AnsibleModule

try:
    # Running example with pip-installed SDK
    import privx_api
except ImportError:
    # Running example without installing SDK
    from utils import load_privx_api_lib_path
    load_privx_api_lib_path()
    import privx_api


def main():
    host_data_spec = {
        'host_data': {
            'type': 'dict',
            'required': True,
            'options': {
                'common_name': {'type': 'str', 'required': True},
                'addresses': {'type': 'list', 'elements': 'str', 'required': False},
                'access_group': {'type': 'str', 'required': False},  # Explicitly mentioned
                'external_id': {'type': 'str', 'required': False},
                'ssh_host_public_keys': {'type': 'list', 'required': False},
                'services': {
                    'type': 'list',
                    'elements': 'dict',
                    'options': {
                        'service': {'type': 'str', 'required': True},
                        'address': {'type': 'str', 'required': True},
                        'port': {'type': 'int', 'required': True},
                        'source': {'type': 'str', 'required': False}
                    }
                },
                'principals': {
                    'type': 'list',
                    'elements': 'dict',
                    'options': {
                        'principal': {'type': 'str', 'required': True},
                        'passphrase': {'type': 'str', 'required': False},
                        'source': {'type': 'str', 'required': False},
                        'roles': {
                            'type': 'list',
                            'elements': 'dict',
                            'options': {
                                'name': {'type': 'str', 'required': True}
                            }
                        }
                    }
                }
            }
        }
    }

    argument_spec = define_argument_spec(host_data_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    result = {
        'changed': False,
        'failed': False,
        'msg': '',
    }

    privx_module = PrivXAnsibleModule(module.params)
    api = privx_module.api

    host_data = module.params['host_data']
    if host_data:
        # Call function to add a host
        add_host(api, module, host_data, result)
    else:
        module.fail_json(msg="No host data provided")

    # Proper exit handling
    if result['failed']:
        module.fail_json(**result)
    else:
        module.exit_json(**result)

def filter_exact_matches(hosts, common_name):
    return [host for host in hosts if host.get('common_name') == common_name]

def update_host(api, module, host_id, existing_host_data, new_host_data, result):

    # Copy current host data, but update with new data where applicable
    updated_host_data = existing_host_data.copy()

    # Update fields from new_host_data, potentially excluding external_id
    for key, value in new_host_data.items():
        if key == 'external_id':
            # Skip overriding external_id unless specifically allowed
            continue
        updated_host_data[key] = value

    # Check if any relevant data has changed before making an update call
    if updated_host_data != existing_host_data:
        update_response = api.update_host(host_id, updated_host_data)
        if update_response._ok:
            result['msg'] = "Host updated successfully."
            result['diff'] = diff_dicts(updated_host_data, existing_host_data)
            result['changed'] = True
            module.exit_json(**result)
        else:
            module.fail_json(msg=f"Host update failed: {update_response._data}")
    else:
        module.exit_json(msg="No update necessary; no data has changed.")

def add_host(api, module, host_data, result):
    # Fetch role mappings only if needed

    hoststore = PrivXHostStore(api)

    # Process roles in host_data
    new_roles = []
    for principal in host_data.get('principals', []):
        if 'roles' in principal:
            for role in principal['roles']:
                try:
                    role_id = PrivXRoleStore.get_role_id_by_input(api, role)
                    new_roles.append({'id': role_id})
                except Exception as e:
                    result['failed'] = True
                    result['msg'] = f"{e}"
                    return

            principal['roles'] = new_roles

    # Process access group
    if 'access_group' in host_data:
        try:
            host_data['access_group_id'] = PrivXAuthorizer.get_access_group_by_input(api, host_data['access_group'])
            del host_data['access_group']
        except Exception as e:
            result['failed'] = True
            result['msg'] = f"{e}"
            return

    # Search for the host by common name
    search_payload = {"common_name": [host_data['common_name']]}
    existing_hosts = api.search_hosts(search_payload=search_payload)

    if existing_hosts.ok:
        if existing_hosts.data.get("count", 0) > 0:
            exact_matches = filter_exact_matches(existing_hosts.data['items'], host_data['common_name'])
            if exact_matches:
                # Host exists, possibly update the host
                host_id = exact_matches[0]["id"]
                msg, changed = update_host(api, module, host_id, exact_matches[0], host_data, result)

                if changed:
                    result['msg'] = msg
                    result['changed'] = True
                    # Fetch the complete host details using the host ID
                    host_details_response = api.get_host(host_id)
                    if host_details_response.status == HTTPStatus.OK:
                        result['host_details'] = host_details_response._data
                        result['msg'] += " Updated successfully and details retrieved."
                    else:
                        result['msg'] += f" Failed to retrieve updated host details: {host_details_response._data}"
                else:
                    result['failed'] = True
                    result['msg'] = msg

        else:
            # Host does not exist, create the host
            create_response = api.create_host(host_data)
            if create_response._ok:  # Assuming _ok is a boolean indicating success
                if 'id' in create_response._data:
                    host_id = create_response._data['id']
                    # Fetch the complete host details using the host ID
                    host_details_response = api.get_host(host_id)

                    if host_details_response.status == HTTPStatus.OK:
                        result['host_details'] = host_details_response._data
                        result['msg'] = "Host created successfully and details retrieved."
                    else:
                        result['failed'] = True
                        result['msg'] = f"Failed to retrieve host details: {host_details_response._data}"
                        result['changed'] = True  # Indicating that a change was successfully made
                else:
                    result['failed'] = True
                    result['msg'] = "Host created but no ID returned in response."
            else:
                result['failed'] = True
                result['msg'] = f"Host creation failed: {create_response._data.get('error', 'Unknown error')}"
        return result

if __name__ == "__main__":
    main()
