import traceback
import os
import json

from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils._text import to_native
from ansible.module_utils.common.collections import is_iterable
from ansible.module_utils.basic import AnsibleModule, missing_required_lib, _load_params
from ansible.module_utils.urls import open_url

HAS_PRIVX = True

try:
    import privx_api
except ImportError:
    PRIVX_IMP_ERR = traceback.format_exc()
    HAS_PRIVX = False

def _get_common_config_spec():
    return {
        'hostname': {'type': 'str', 'required': True},
        'hostport': {'type': 'int', 'required': True},
        'ca_cert': {'type': 'str', 'required': True},
        'oauth_client_id': {'type': 'str', 'required': True},
        'oauth_client_secret': {'type': 'str', 'required': True},
        'api_client_id': {'type': 'str', 'required': True},
        'api_client_secret': {'type': 'str', 'required': True},
    }

def define_argument_spec(module_specific_argument_spec):
    config_spec = _get_common_config_spec()
    _argument_spec = {
        'config': {
            'type': 'dict',
            'required': True,
            'options': config_spec
        }
    }
    _argument_spec.update(module_specific_argument_spec)

    return _argument_spec

def diff_dicts(dict1, dict2):
    """
    Compare two dictionaries and return their differences.
    """
    diff = {}
    # Check keys present in dict1 but not in dict2
    for key in dict1.keys():
        if key not in dict2:
            diff[key] = {'old': dict1[key], 'new': None}
    # Check keys present in dict2 but not in dict1
    for key in dict2.keys():
        if key not in dict1:
            diff[key] = {'old': None, 'new': dict2[key]}
    # Check keys present in both dicts
    for key in dict1.keys() & dict2.keys():
        if dict1[key] != dict2[key]:
            diff[key] = {'old': dict1[key], 'new': dict2[key]}
    return diff

class PrivXAnsibleModule(object):
    def __init__(self, module_params):
        # Define the argument spec within the class using static methods or directly here
        self.module = AnsibleModule(
            argument_spec=define_argument_spec(module_params),
            supports_check_mode=True
        )
        self.config = module_params.get('config', {})

        # Check if the privx_api library is available
        if not HAS_PRIVX:
            self.module.fail_json(
                msg=missing_required_lib("privx_api"),
                exception=PRIVX_IMP_ERR
            )

        # Initialize the API client
        self._initialize_privx_api()
        self._authenticate_privx_api()

    @property
    def api(self):
        return self.privx

    def _initialize_privx_api(self):
        try:
            self.privx = privx_api.PrivXAPI(
                self.config.get('hostname', ''),
                self.config.get('hostport', ''),
                self._get_certificate_content(self.config.get('ca_cert', '')),
                self.config.get('oauth_client_id', ''),
                self.config.get('oauth_client_secret', ''),
            )
        except Exception as e:
            self.module.fail_json(
                msg=f"Failed to establish connection to PrivX API: {e}"
            )

    def _authenticate_privx_api(self):
        try:
            self.privx.authenticate(
                self.config.get('api_client_id', ''),
                self.config.get('api_client_secret', '')
            )
        except Exception as e:
            self.module.fail_json(
                msg=f"Failed to authenticate to the PrivX API: {e} {api_client_id} {api_client_secret}"
            )

    def _get_certificate_content(self, ca_cert):
        if os.path.isfile(ca_cert):
            with open(ca_cert, 'r') as file:
                return file.read()
        else:
            return ca_cert
