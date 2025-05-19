from django.conf import settings
import jwt, logging

logger= logging.getLogger('access')
logger.propagate= False

def get_uuid(token):
    """
    Function to get the uuid from the token which is using RS256 algorithm.
    """
    try:
        decoded_data = jwt.decode(jwt=token, algorithms=["HS256"])
        return str(decoded_data['id'])
    except Exception as e:
        logger.info("Failed to get the uuid from the token %s",str(e))
        return "AnonymousUser"