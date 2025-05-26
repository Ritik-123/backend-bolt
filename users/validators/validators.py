from users.models import User
import re
from rest_framework import serializers
from rest_framework.exceptions import NotFound



class EmailValidators():

    """
    *Check given email is exist or not***
    """
    
    def emailExists(cls, email):
        email= email.lower()
        if User.objects.emailExists(email):
            raise serializers.ValidationError('Email already exists')

    def __call__(self, email):
        self.emailExists(email)


class NameValidator:
    """
    Validator class for ensuring names meet specific criteria.

    The name must:
    - Be between 5 and 20 characters long
    - Consist only of alphabets and spaces
    - Not contain any whitespace characters.

    Methods:
    --------
    __call__(name: str):
        Raises a serializers.ValidationError if the name does not meet the criteria.
    """

    # Error messages for specific validation failures
    MIN_LENGTH_ERROR = "The username must be at least 5 characters long and maximum 20 characters long."
    NAME_ERROR = "The username may only contain alphanumeric characters (a-z, A-Z, 0-9), underscores (_),and hyphens (-)."
    # SINGLE_SPACE_ERROR = "The usename must not contain whitespace character."
    SINGLE_SPACE_ERROR = "The username must not contain leading or trailing whitespace characters."
    START_CHARACTER_ERROR = "The username must start with a letter (a-z or A-Z)."
    END_CHARACTER_ERROR = "The username must not end with an underscore, hyphen, or special character."
    
    def __init__(self):
        self.rules = [
        ( re.compile('^.{5,20}$'),self.MIN_LENGTH_ERROR),
        ( re.compile('^[a-zA-Z0-9_-]+$'),self.NAME_ERROR),
        ( re.compile('^[a-zA-Z]'),self.START_CHARACTER_ERROR),        
        ( re.compile(r'^.*[^\s~!@=#$%^&*()_+{}:"<>?|\\]$'),self.END_CHARACTER_ERROR),
        (re.compile(r'^\S.*\S$|^\S$'), self.SINGLE_SPACE_ERROR),
        
        ]
    def validate(self,name: str) -> None:
        """
        Validates the provided username against the defined rules.

        Parameters
        ----------
        name : str
            The name to validate.

        Raises
        ------
        ValidationError
            If the name fails any of the validation criteria.
        """
        if User.objects.usernameExists(name):
            raise serializers.ValidationError('Username already exists')
        for regex, error_message in self.rules:
            test = regex.search(name)
            if not regex.search(name):
                raise serializers.ValidationError(error_message)


    def __call__(self, name: str) -> None:
        """
        Validates the provided name to ensure it meets the specified criteria.

        Parameters
        ----------
        name : str
            The name to validate.

        Raises
        ------
        serializers.ValidationError
            If the name does not meet the specified criteria.
        """
        self.validate(name)


class PasswordValidator:
    """
    Validator class for ensuring passwords meet specific security criteria.

    The password must:
    - Be between 8 and 32 characters long.
    - Contain at least one lowercase letter.
    - Contain at least one uppercase letter
    - Contain at least one digit
    - Contain at least one special character from the set !@#$%^&*()_+[]{}|;:',.<>?/`~
    - Not contain any whitespace characters.
    """

    # Error messages for specific validation failures
    MIN_LENGTH_ERROR = "The password must be at least 8 characters long and maximum 32 characters long."
    UPPERCASE_ERROR = "The password must contain at least one uppercase letter."
    LOWERCASE_ERROR = "The password must contain at least one lowercase letter."
    NUMBER_ERROR = "The password must contain at least one number."
    SPECIAL_CHARACTER_ERROR = "The password must contain at least one special character."
    SINGLE_SPACE_ERROR = "The password must not contain whitespace character."

    def __init__(self):
        self.rules = [
        ( re.compile('^.{8,32}$'),self.MIN_LENGTH_ERROR),
        ( re.compile('^(?=.*[A-Z]).+$'),self.UPPERCASE_ERROR),
        ( re.compile('^(?=.*[a-z]).+$'),self.LOWERCASE_ERROR),
        ( re.compile('^(?=.*\\d).+$'),self.NUMBER_ERROR),
        ( re.compile('^(?=.*[!@#$%^&*.()]).+$'),self.SPECIAL_CHARACTER_ERROR),
        ( re.compile('^(?!.*\\s).+$'),self.SINGLE_SPACE_ERROR)
        ]
    
    def validate(self, password: str) -> None:
        """
        Validates the provided password against the defined rules.

        Parameters
        ----------
        password : str
            The password to validate.

        Raises
        ------
        ValidationError
            If the password fails any of the validation criteria.
        """
        for regex, error_message in self.rules:
            if not regex.search(password):
                raise serializers.ValidationError(error_message)

    def __call__(self, password: str) -> None:
        """
        Allows the validator to be used as a callable, validating the provided password.

        Parameters
        ----------
        password : str
            The password to validate.

        Raises
        ------
        ValidationError
            If the password does not meet the specified criteria.
        """
        self.validate(password)

class UidValidator:

    """
    **Used to check the User is exists with given uid.**\n
    Input:
        uid : uuuid type. 
    """

    def userExistUid(self, uid):
        if not User.objects.filter(id= uid).exists():
            raise NotFound(f'User not found with id : {uid}')
        
    def __call__(self, uid):
        self.userExistUid(uid)


class ForgotPasswordEmailValidator:
    """
    **Used to check the email is exists or not.**\n
    Input:
        email : str type. 
    """

    def userExistEmail(self, email):
        if not User.objects.filter(email= email).exists():
            raise NotFound(f'User not found with email : {email}')
        
    def __call__(self, email):
        self.userExistEmail(email)
        