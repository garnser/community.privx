from ansible_collections.garnser.privx.plugins.module_utils.privx_utils import PrivXAnsibleModule

class PrivXHostModule(PrivXAnsibleModule):
    def __init__(self, module):
        super().__init(module)
