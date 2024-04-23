class PrivXAuthorizer():

    @staticmethod
    def get_access_groups(api):
        """Fetch all access groups and return a mapping of names to IDs and a set of valid IDs."""
        response = api.get_access_groups()
        try:
            if response._ok:
                access_groups_mapping = {group['name']: group['id'] for group in response.data['items']}
                valid_ids = {group['id'] for group in response.data['items']}
                return access_groups_mapping, valid_ids
            else:
                _display.warning("Failed to fetch access groups from PrivX API.")
                return {}, set()
        except Exception as e:
            _display.error("Error fetching access groups: %s" % str(e))
            return {}

    @staticmethod
    def get_access_group_by_input(api, input_string):

        access_groups_mapping, valid_access_group_ids = PrivXAuthorizer.get_access_groups(api)

        if input_string in access_groups_mapping:
            ag_id = access_groups_mapping[input_string]
        elif input_string in valid_access_group_ids:
            ag_id = input_string
        else:
            raise Exception("No matching access group found for input: {}".format(input_string))

        return ag_id
