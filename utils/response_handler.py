from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(data={}, message="Success"):
    """Standard success response format"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": message,
            "data": jsonable_encoder(data),
        },
    )


def error_response(message="Error", status_code=500):
    return JSONResponse(
        content={"status": "error", "message": message}, status_code=status_code
    )
