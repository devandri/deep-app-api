from ninja import Schema
from typing import Optional, Any
from datetime import datetime, timezone

class ErrorResponse(Schema):
    code: str
    message: str
    details: Optional[dict] = None

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _envelope(
    *,
    data: Any = None,
    message: str = "OK",
    code: Optional[int] = None,
    status: str = "success"
) -> dict:
    return {
        "status": status,
        "code": code,
        "message": message,
        "data": data,
        "timestamp": _now_iso()
    }
    
def success(data=None, message="OK", code=None) -> dict:
    return _envelope(data=data, message=message, code=code)

def created(data=None, message="Created") -> dict:
    return _envelope(data=data, message=message, code=201)

def error(message="Request failed", code: int = 400, errors=None) -> dict:
    return _envelope(
        data=None, message=message, code=code, status="error"
    ) | {
        "errors": errors
    } if errors else _envelope(
        data=None, message=message, code=code, status="error"
    )
    
def paginated(items, pagination: dict, message="OK") -> dict:
    """Wrap list results into the nested data shape."""
    return _envelope(
        data={"items": items, "pagination": pagination},
        message=message,
        code=None
    )