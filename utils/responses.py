from ninja import Schema
from typing import Optional

class ErrorResponse(Schema):
    code: str
    message: str
    details: Optional[dict] = None
