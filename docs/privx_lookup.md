# privx_lookup Lookup Plugin

The `privx_lookup` lookup plugin allows you to interact with the PrivX Python SDK to perform various actions or retrieve data based on the terms provided. This plugin requires certain configuration keys and can dynamically call methods utilizing the PrivX API.

## Synopsis

This lookup plugin dynamically calls methods available in the PrivX Python SDK, passing parameters and returning results as needed.

## Requirements

- `privx_api` Python module must be installed.
- PrivX API must be accessible from the Ansible controller.

## Parameters

| Parameter   | Required | Description                                  | Type  |
|-------------|----------|----------------------------------------------|-------|
| `config`    | Yes      | Dictionary containing API connection details.| dict  |
| `filter`    | No       | Additional filter to pass to the API calls.  | string or list |

## Configuration Keys

The `config` dictionary must contain the following keys:

- `hostname`: The hostname of the PrivX server.
- `hostport`: The port number to connect to on the PrivX server.
- `ca_cert`: Path to the CA certificate file or CA certificate string for HTTPS verification.
- `oauth_client_id`: The OAuth client ID for authentication.
- `oauth_client_secret`: The OAuth client secret for authentication.
- `api_client_id`: The API client ID for authentication.
- `api_client_secret`: The API client secret for authentication.

## Examples

### Example 1: Retrieving roles

```yaml
- name: Retrieve roles from PrivX
  debug:
    msg: "{{ lookup('community.privx.privx_lookup', 'get_roles', config=privx_config, filter='privx-user') }}"
  vars:
    privx_config:
      hostname: 'privx.example.com'
      hostport: 443
      ca_cert: '/path/to/cert.pem'
      oauth_client_id: 'your_oauth_client_id'
      oauth_client_secret: 'your_oauth_client_secret'
      api_client_id: 'your_api_client_id'
      api_client_secret: 'your_api_client_secret'
```

### Example 2: Using without filter
```yaml
- name: Call a method without filter
  debug:
    msg: "{{ lookup('community.privx.privx_lookup', 'other_method', config=privx_config) }}"
```

## Return Values
| Key | Description | Type |
|----|----|----|
| data | Data returned from the PrivX API method call. | list or dict |

## Authors
Jonathan Petersson <jpetersson@garnser.se>
