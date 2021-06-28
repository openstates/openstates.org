import requests
from openstates import metadata


def coords_to_divisions(lat, lng):
    url = f"https://v3.openstates.org/divisions.geo?lat={lat}&lng={lng}"
    divisions = []
    try:
        data = requests.get(url).json()
        for d in data["divisions"]:
            divisions.append(d["id"])
        divisions.append(metadata.lookup(abbr=d["state"]).division_id)
    except Exception:
        # be very resilient
        pass
    return divisions
