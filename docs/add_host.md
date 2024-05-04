# add_host Plugin

This document describes the usage and parameters of the `add_host` action plugin.

## Synopsis

This plugin allows you to add or update hosts in PrivX.

## Parameters

- `hostname`: The hostname of the PrivX instance.
- `host_data`: A dictionary containing data about the host.

## Examples

```yaml
- name: Add host to PrivX
  garnser.privx.add_host:
    privx_config:
      hostname: 'privx.ssh.com'
      hostport: 443
      ca_cert: 'privx.crt'
      oauth_client_id: 'privx-external'
      oauth_client_secret: 'XXXXXXXXXXXXXXXXXXXXXX'
      api_client_id: 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
      api_client_secret: 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    host_data:
      common_name: "host.privx.ssh.com"
      addresses: ["host.privx.ssh.com", "192.168.0.10"]
      access_group: "sysadmin"
      services:
        - service: "SSH"
          address: "192.168.0.10"
          port: 22
          source: "UI"
      principals:
        - principal: "root"
          passphrase: "secret"
          source: "UI"
          roles:
            - name: "privx-user"
```

## Return Values


### Additional Tips

- **Versioning**: Keep your collection version updated in the `galaxy.yml` whenever you make changes.
- **Contributing Guidelines**: Consider adding a `CONTRIBUTING.md` file explaining how others can contribute to your collection.
- **Testing**: Document how to run tests for your collection if applicable.
