from dataclasses import dataclass, field
from typing import Any
from rest_framework.response import Response


@dataclass
class BaseResponse:
    """
    Base class for each Response.
    Input:
        -> We have to pass the data and status code. 
    """
    status_code: int
    data: Any= field(default= None)

class SuccessResponse(BaseResponse):
    """
    We inherit the Base response class. 
    Through which i can get data and status code.
    
    In this api we return the Success api response.
    """

    def __call__(self):
        return self.response()

    def response(self):
        return Response(data= self.data, status= self.status_code)

class FailureResponse(BaseResponse):
    """
    We inherit the Base response class. 
    Through which i can get data and status code.
    
    In this api we return the Failure api response.
    """

    def __init__(self, message):
        self.message= message

    def __call__(self):
        return self.response()

    def response(self):
        return Response(message= self.message, status= self.status_code)    
    