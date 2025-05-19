from fastapi import APIRouter
import platform
import socket
from utils.response_handler import success_response, error_response

router = APIRouter(prefix="/common", tags=["Common APIs"])


@router.get(
    "/health",
    summary="Service Health Check",
    response_description="Service health status",
)
async def health_check():
    """
    Health Check

    Performs a basic health check to ensure that the API service is operational.

    - **Returns:** A JSON object with the service status (e.g., "up").
    - **Success Response:**
      - `status`: `"success"`
      - `message`: `"Service is healthy"`
      - `data`: `{"status": "up"}`

    - **Error Response:**
      - `status`: `"error"`
      - `message`: Error message string

    This endpoint can be used for monitoring and health check purposes.
    """
    try:
        return success_response({"status": "up"}, message="Service is healthy")
    except Exception as e:
        return error_response(f"Health check failed: {str(e)}")


@router.get(
    "/ping",
    summary="Ping the Server",
    response_description="Ping response to check server connectivity",
)
async def ping():
    """
    Ping

    Basic ping endpoint to test server responsiveness and connectivity.

    - **Returns:** A simple response to indicate that the server is responsive.
    - **Success Response:**
      - `status`: `"success"`
      - `message`: `"Success"`
      - `data`: `{"ping": "pong"}`

    Useful for quick server health and connectivity checks.
    """
    return success_response({"ping": "pong"})


@router.get(
    "/info",
    summary="System Information",
    response_description="Detailed system and environment info",
)
async def system_info():
    """
    System Information

    Retrieves essential system information, including:
    - Hostname: The server's hostname.
    - Platform: Operating system type.
    - Platform Version: Version of the operating system.
    - Architecture: System architecture (e.g., x86_64).
    - Python Version: Version of Python running the service.

    - **Returns:** A JSON object with system information.
    - **Success Response:**
      - `status`: `"success"`
      - `message`: `"Success"`
      - `data`: Dictionary containing the system information.

    - **Error Response:**
      - `status`: `"error"`
      - `message`: Error message string

    Use this endpoint to quickly access the server's environment and system details.
    """
    try:
        info = {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
        }
        return success_response(info)
    except Exception as e:
        return error_response(f"Failed to retrieve system info: {str(e)}")


@router.get("/uptime")
async def uptime():
    """
    Get server uptime information.

    This endpoint retrieves the system uptime from the `/proc/uptime` file,
    which is available on Linux-based systems. The uptime is represented as
    the total number of seconds the system has been running since it was started.
    Additionally, it calculates the system boot date based on the current time
    and the uptime duration.

    Returns:
        JSON object containing:
        - `uptime_seconds`: Total uptime in seconds.
        - `uptime_minutes`: Total uptime in minutes.
        - `uptime_hours`: Total uptime in hours.
        - `uptime_days`: Total uptime in days.
        - `boot_date`: The date and time when the system was started.

    Example Response:
    {
        "uptime_seconds": 123456.78,
        "uptime_minutes": 2057.61,
        "uptime_hours": 34.29,
        "uptime_days": 1.43,
        "boot_date": "2024-03-28 08:15:32"
    }

    Raises:
        - 500 Internal Server Error: If uptime data cannot be retrieved.
    """
    try:
        from datetime import datetime, timedelta

        # Open the /proc/uptime file to read uptime data
        with open("/proc/uptime", "r") as f:
            # The file contains two floats: uptime and idle time (in seconds)
            uptime_seconds = float(f.readline().split()[0])

            # Calculate the boot date by subtracting uptime from the current time
            boot_date = datetime.now() - timedelta(seconds=uptime_seconds)

            # Convert uptime to various units
            uptime_minutes = uptime_seconds / 60
            uptime_hours = uptime_seconds / 3600
            uptime_days = uptime_seconds / 86400

            # Prepare the response with detailed uptime information
            uptime_info = {
                "uptime_seconds": round(uptime_seconds, 2),
                "uptime_minutes": round(uptime_minutes, 2),
                "uptime_hours": round(uptime_hours, 2),
                "uptime_days": round(uptime_days, 2),
                "boot_date": boot_date.strftime("%Y-%m-%d %H:%M:%S"),
            }

            return success_response(
                uptime_info, message="Uptime retrieved successfully"
            )

    except Exception as e:
        # Handle any errors that occur while retrieving uptime
        return error_response(f"Failed to retrieve uptime: {str(e)}")
