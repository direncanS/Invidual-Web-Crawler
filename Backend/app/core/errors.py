from fastapi import HTTPException, status


def error_response(code: str, message: str, http_status: int = status.HTTP_400_BAD_REQUEST):
    raise HTTPException(
        status_code=http_status,
        detail={"error": {"code": code, "message": message, "http_status": http_status}},
    )


def not_implemented_error(message: str):
    error_response("not_implemented", message, status.HTTP_501_NOT_IMPLEMENTED)
