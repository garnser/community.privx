import os
import inspect

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

try:
    import privx_api
except ImportError:
    PRIVX_IMP_ERR = traceback.format_exc()
    HAS_PRIVX = False

REQUIRED_CONFIG_KEYS = [
    'hostname', 'hostport', 'ca_cert',
    'oauth_client_id', 'oauth_client_secret',
    'api_client_id', 'api_client_secret'
]

def initialize_privx_api(config):
    privx = None
    try:
        privx = privx_api.PrivXAPI(
            config.get('hostname', ''),
            config.get('hostport', ''),
            get_certificate_content(config.get('ca_cert', '')),
            config.get('oauth_client_id', ''),
            config.get('oauth_client_secret', ''),
        )
        try:
            privx.authenticate(
                config.get('api_client_id', ''),
                config.get('api_client_secret', '')
            )
        except Exception as e:
            Display().error(f"Failed to authenticate to the PrivX API: {e} {config.get('api_client_id')} {config.get('api_client_secret')}")

    except Exception as e:
        Display().error(f"Failed to establish connection to PrivX API: {e}")

    return privx

def get_certificate_content(ca_cert):
    if os.path.isfile(ca_cert):
        with open(ca_cert, 'r') as file:
            return file.read()
    else:
        return ca_cert

def validate_config(config):
    missing_keys = [key for key in REQUIRED_CONFIG_KEYS if key not in config]
    if missing_keys:
        Display().error(f"Missing configuration keys: {', '.join(missing_keys)}")
        return False
    return True

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        config = kwargs.get("config")
        filter_arg = kwargs.get("filter", None)

        if not validate_config(config):
            Display().error("Configuration validation failed.")
            raise AnsibleError("Invalid configuration for PrivX API.")

        if not isinstance(terms, list):
            terms = [terms]

        privx = initialize_privx_api(config)
        if privx is None:
            Display().error("PrivX API object initialization failed, check logs for details.")
            return []

        results = []
        for term in terms:
            func = getattr(privx, term, None)
            try:
                if func and callable(func):
                    params = inspect.signature(func).parameters
                    if params and filter_arg is not None:
                        results.append(func(filter_arg).data)
                    else:
                        results.append(func().data)
                else:
                    Display().error(f"No such function '{term}' available on PrivX API.")
                    continue
            except Exception as e:
                Display().error(f"Error executing '{term}' with arguments '{filter_arg}': {str(e)}")

        return results
