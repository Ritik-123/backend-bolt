from django.contrib.auth.models import BaseUserManager

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