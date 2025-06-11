# from users.models import Permission, RolePermission
# from django.http import JsonResponse
# # from ..models import User
# from utils.base import JWTManager,get_uuid
# from django.urls import reverse, resolve
# # from users.services.userservice import UserService
# import re, logging

# logger= logging.getLogger('server')
# logger.propagate= False

# class RBACMiddleware:
#     """
#     It is used to check the permission is assigned to role or not.
    
#     If YES:
#         -> It return True.
#         -> Requested user can able to perform operation.
    
#     else:
#         -> It return False.
#         -> raise permission denied (forbidden) error : 'You do not have permission to perform this action'   
#     """

#     def __init__(self, get_response):
#         self.get_response = get_response
        
#     def check_permissions(self, request):
#         api_without_token= ('login', 'refresh', 'forgot-password', 'forgot-password-link', 'forgot-password-key', 'forgot-password-token', 'verify-account', 'verify-account-uuid', 'schema', 'swagger', 'redoc', 'admin', 'index') #'reset-password'
#         resolve_match= resolve(request.path)
#         viewname= resolve_match.url_name
#         if viewname:
#             if viewname in api_without_token:
#                 return True
#         token = request.META.get('HTTP_AUTHORIZATION')
#         if not token or token == "" or token == '' or token == '{{access}}' or token == None:
#             return False
        
#         if token!=None :
#             uuid = get_uuid(str(token[7::]))
#         else:
#             uuid = "AnonymousUser"
#         request.user=UserService.get_user_by_uuid(uuid)
#         user_obj = request.user
#         if not user_obj:
#             return False
#         if user_obj.user_has_roles.all()[0].rid.name == 'superadmin' and user_obj.user_has_roles.all()[0].rid.is_staff == True: 
#             return True
#         role_queryset= user_obj.user_has_roles.all()
#         if not role_queryset:
#             return False
#         role_objs= []
#         for obj in role_queryset:
#             if obj.rid.name == 'superadmin' and obj.rid.is_staff == True: 
#                 return True 
#             role_objs.append(obj.rid)
        
#         for role_obj in role_objs:
#             if viewname:
#                 api_method= request.method
#                 if api_method == 'GET':
#                     perm_name= f"view_{viewname}"
#                     check_perm= Permission.objects.filter(codename= perm_name).first()
#                     if check_perm:
#                         allow_obj= RolePermission.objects.filter(rid= role_obj.rid, permid= check_perm.permid).first()
#                         if allow_obj:
#                             return True
#                         continue
#                     return True
#                 if api_method == 'POST':
#                     perm_name= f"add_{viewname}"
#                     check_perm= Permission.objects.filter(codename= perm_name).first()
#                     if check_perm:
#                         allow_obj= RolePermission.objects.filter(rid= role_obj.rid, permid= check_perm.permid).first()
#                         if allow_obj:
#                             return True
#                         continue
#                     return True
#                 if api_method == 'PATCH' or api_method == "PUT":
#                     perm_name= f"change_{viewname}"
#                     check_perm= Permission.objects.filter(codename= perm_name).first()
#                     if check_perm:
#                         allow_obj= RolePermission.objects.filter(rid= role_obj.rid, permid= check_perm.permid).first()
#                         if allow_obj:
#                             return True
#                         continue
#                     return True
#             else:
#                 return True
#         return False
    
#     def __call__(self, request):
#         if not self.check_permissions(request):
#             data= {
#                 "type": "PermissionDenied",
#                 "message": 'You do not have permission to perform this action',
#                 "field_name": None,  
#                 "status_code": 403
#             }
#             return JsonResponse(data, status= 403)
#         response = self.get_response(request)
#         return response