from enum import Enum

from django.http import JsonResponse


def return_entities(view):
    def decorated_view(request):
        err, entities = view(request)
        if err is not None:
            return JsonResponse(err.__dict__, status=err.status_code, safe=False)
        else:
            return JsonResponse([entity.__dict__ for entity in entities], status=200, safe=False)

    return decorated_view


class Error:
    def __init__(self, status_code, message, error_code):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code


class ErrorCode(Enum):
    INTERNAL_SERVER_ERROR = 1


class InternalServerError(Error):
    def __init__(self):
        super().__init__(500, 'Internal server error', ErrorCode.INTERNAL_SERVER_ERROR.value)