import logging

from django.http import Http404
from ninja import NinjaAPI
from ninja.errors import AuthenticationError, ValidationError

logger = logging.getLogger(__name__)

class ApiError(Exception):
    def __init__(self, message: str, code: str = "error", status: int = 400, errors=None):
        self.message = message
        self.code = code
        self.status = status
        self.errors = errors or []

def _error_body(message: str, code: str, errors=None) -> dict:
    return {
        "success": False,
        "message": message,
        "code": code,
        "errors": errors or []
    }
    
def register_exception_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(ApiError)
    def handle_api_error(request, exc: ApiError):
        return api.create_response(
            request, _error_body(exc.message, exc.code, exc.errors), status=exc.status
        )
        
    @api.exception_handler(ValidationError)
    def handle_validation(request, exc: ValidationError):
        errors = [
            {"field": ".".join(str(p) for p in e["loc"][1:]) or None, "message": e["message"]}
            for e in exc.errors
        ]
        return api.create_response(
            request, _error_body("Validation failed", "validation_error", errors), status=422
        )
        
    @api.exception_handler(AuthenticationError)
    def handle_auth(request, exc):
        return api.create_response(
            request, _error_body("Not authenticated", "unaunthenticated"), status=401
        )
        
    @api.exception_handler(Http404)
    def handle_404(request, exc):
        return api.create_response(
            request, _error_body("Resource not found", "not_found"), status=404
        )
        
    @api.exception_handler(Exception)
    def handle_unexpected(request, exc):
        logger.exception("Unhandled error")
        return api.create_response(
            request, _error_body("Internal server error", "server_error"), status=500
        )