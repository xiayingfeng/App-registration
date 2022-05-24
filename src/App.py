from numpy import outer
import Owner


class App:

    # created: str            # Created on
    # secrets: str            # Certificates & secrets

    # name: str               # Display name
    # app_id: str             # Application (client)ID
    # obj_id: str             # Object ID
    # dir_id: str             # Directory ID
    # type: str               # Supported account type
    # cred: str               # Client credential
    # re_uri: str             # Redirect URIs
    # app_id_uri: str         # Application ID URI
    # app_local: str          # Managed application in local directory

    # owners: list(Owner)     # Owners

    def __init__(self, created: str = "", secrets: str = "", name: str = "",
                 app_id: str = "", obj_id: str = "", dir_id: str = "",
                 type: str = "", cred: str = "", re_uri: str = "",
                 app_id_uri: str = "", app_local: str = "", owners: list = None):
        self.created = created
        self.secrets = secrets
        self.name = name
        self.app_id = app_id
        self.obj_id = obj_id
        self.dir_id = dir_id
        self.type = type
        self.cred = cred
        self.re_uri = re_uri
        self.app_id_uri = app_id_uri
        self.app_local = app_local
        self.owners = owners

    def get_owners(self):
        out_owners = list()
        for owner in self.owners:
            info: str = owner.name + ": " + owner.u_name
            out_owners.append(info)
        return out_owners
