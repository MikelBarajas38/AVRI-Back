from rest_framework.exceptions import APIException
from rest_framework import status

class RagflowException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'RAGFLOW service is unavailable'
    default_code = 'service_unavailable'
