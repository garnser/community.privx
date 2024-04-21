class PrivXRoleStore():

    @staticmethod
    def get_roles(api):
        """Fetch all roles and return a mapping of names to IDs and a set of valid IDs."""
        response = api.get_roles()
        try:
            if response._ok:
                roles_mapping = {role['name']: role['id'] for role in response.data['items']}
                valid_ids = {role['id'] for role in response.data['items']}
                return roles_mapping, valid_ids
            else:
                _display.warning("Failed to fetch roles from PrivX API.")
                return {}, set()
        except Exception as e:
            _display.error("Error fetching roles: %s" % str(e))
            return {}

    @staticmethod
    def get_role_id_by_input(api, input_string):

        roles_mapping, valid_role_ids = PrivXRoleStore.get_roles(api)

        if 'name' in input_string and input_string['name'] in roles_mapping:
            role_id = roles_mapping[input_string['name']]
        elif 'id' in input_string and input_string['id'] in valid_role_ids:
            role_id = input_string['id']
        else:
            raise Exception("No matching role found for input: {}".format(input_string))

        return role_id
