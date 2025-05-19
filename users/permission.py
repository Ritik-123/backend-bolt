from rest_framework.exceptions import PermissionDenied



class CheckUserPermission:

    """
    **It checks the requested user has permission or not.**\n
    """

    def userHasAccess(self, userobj, id):
        if userobj.is_staff == True:
            return
        if userobj.id == id:
            return
        raise PermissionDenied()

    def __call__(self, userobj, id):
        self.userHasAccess(userobj, id)