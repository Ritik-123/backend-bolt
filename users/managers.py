from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    """
    def create_user(self, email, username, password=None):
        """
        Creates and returns a user with an email, username and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None):
        """
        Creates and returns a superuser with an email, username and password.
        """
        if not email:
            raise ValueError('Superusers must have an email address')
        if not username:
            raise ValueError('Superusers must have a username')
        if not password:
            raise ValueError('Superusers must have a password')

        user = self.create_user(
            email,
            username=username,
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    def emailExists(self, email):
        """
        **Used to return boolean value on the basis of email exists in a user table.**\n
        """
        return self.filter(email= email).exists()
    
    def usernameExists(self, username):
        """
        **Used to return boolean value on the basis of username exists in a user table.**\n
        """
        return self.filter(username= username).exists()
    
class RoleManager(models.Manager):
    """
    Return queries related with Role model
    """
    
    def role_exists_rid(self, rid):
        """
        It checks the role exists but exclude superadmin.
        """
        return self.filter(rid=rid).exclude(name= 'superadmin', is_staff= True).exists()
    
    def role_object_with_rid(self, rid):
        """
        It checks the role exists with rid.
        """
        return self.filter(rid= rid).first()
    
    def role_exists_name(self, name, rid):
        """
        It checks the role exists with name but exclude superadmin.
        condition: 
            -> if same role name in role update api then we have to exclude this row also.
        """
        return self.exclude(Q(name= 'superadmin', is_staff= True) | Q(rid= rid)).filter(name= name).exists()
        
    def single_role(self, rid):
        """
        Used to return the single role object.
        """
        return self.filter(rid= rid).first()
    
    def exclude_superadmin(self):
        """
        Used to return all the roles except superadmin.
        """
        return self.exclude(name= 'superadmin', is_staff= True).all()
    
    def role_by_name(self, name):
        """
        Used to filter role by name.
        """
        return self.filter(name= name).first()

    def role_count(self):
        """
        Used to return the count of all roles.
        """
        return self.exclude(name= 'superadmin', is_staff= True).count()
    
    def all_roles(self):
        """
        return all the roles objects.
        """
        return self.all()
    
    def role_reports_to(self, reports_to):
        """
        Used to return single role based on reports to.
        """
        return self.filter(reports_to= reports_to).select_related('reports_to').first()
    
    def role_reports_to_count(self, reports_to):
        """
        Return the count of role reports to: 
        for ex: how many roles report to role manager
        """
        return self.filter(reports_to= reports_to).count()
    
    def create_role(self, **kwargs):
        """
        Used to create role.
        Inside kwargs we extract all the keys data which is necessary.
        """
        name= kwargs.get('name')
        description= kwargs.get('description')
        level= kwargs.get('level')
        created_by= kwargs.get('created_by')
        reports_to= kwargs.get('reports_to')
        return self.create(name= name, description= description, level= level, created_by= created_by, reports_to= reports_to)

    def update_role(self, instance, **kwargs):
        """
        Used to update role data.
        Inside kwargs we extract all the keys data which is necessary
        """
        name= kwargs.get('name')
        setattr(instance, 'name', name)
        description= kwargs.get('description')
        setattr(instance, 'description', description)
        level= kwargs.get('level')
        setattr(instance, 'level', level)
        reports_to= kwargs.get('reports_to')
        setattr(instance, 'reports_to', reports_to)
        instance.save()

class PermissionsManager(models.Manager):
    """
    Return objects related with Permission model.
    """

    def permissions_count(self):
        """"
        It return the count of all entries in permission table.
        """
        return self.all().count()
    
    def delete_all_permissions(self):
        """
        Used to delete all permissions.
        """
        return self.all().delete()

    def permission_bulk_create(self, instances):
        """
        Used to create bulk entries.
        Input : list of instances
        """
        return self.bulk_create(instances)

    def permission_exists(self, permid):
        return self.filter(permid= permid).exists()

    def single_permission(self, permid):
        return self.filter(permid= permid).first()

    def all_permissions(self):
        return self.all()

    def return_list_objects(self, ids_list):
        """
        return all the permission objects present on the basis of permid present inside list.
        """
        return self.filter(permid__in= ids_list)
    
class RolePermissionsManager(models.Manager):
    """
    Return queries related with Role Permission Model.
    """

    def role_exists(self, rid):
        return self.filter(rid= rid).exists()

    def role_permission_exists(self, pk):
        return self.filter(pk=pk).exists()

    def single_role_permission(self, rid):
        """
        return a queryset of all objects related with rid.
        """
        return self.filter(rid= rid).select_related('rid', 'permid')
    
    def object_by_rid_permid(self, rid, permid):
        """
        Used to return boolean value on the basis of rid, permid
        """
        return self.filter(rid= rid, permid= permid).exists()

    def all_Role_permissions(self):
        return self.all()