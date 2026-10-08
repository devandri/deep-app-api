def ok(data=None, message: str = "OK") -> dict:
    return {
        "success": True,
        "message": message,
        "data": data
    }