import requests


def coords_to_divisions(lat, lng):
    url = f"https://v3.openstates.org/divisions.geo?lat={lat}&lng={lng}"
    try:
        data = requests.get(url).json()
        return [d["id"] for d in data["divisions"]]
    except Exception:
        # be very resilient
        return []
