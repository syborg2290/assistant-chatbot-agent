import requests


def get_user_location_from_ip(ip: str) -> dict:
    try:
        response = requests.get(f"http://ipinfo.io/{ip}/json")
        data = response.json()
        return {
            "ip": ip,
            "city": data.get("city", ""),
            "region": data.get("region", ""),
            "country": data.get("country", ""),
            "timezone": data.get("timezone", ""),
            "loc": data.get("loc", ""),  # "latitude,longitude"
        }
    except Exception as e:
        return {"error": str(e)}
