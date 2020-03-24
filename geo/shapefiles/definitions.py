"""
Configuration describing the shapefiles to be loaded.
"""
# from django.contrib.gis.gdal.error import OGRIndexError
from datetime import date
import boundaries
import os
import us

OGRIndexError = Exception

states = [s for s in us.STATES_AND_TERRITORIES if s not in us.OBSOLETE]
state_fips = {s.fips: s.abbr.lower() for s in states}


def tiger_namer(feature):
    global OGRIndexError
    global state_fips

    try:
        fips_code = feature.get("STATEFP")
    except OGRIndexError:
        fips_code = feature.get("STATEFP10")

    try:
        name = feature.get("NAMELSAD")
    except OGRIndexError:
        name = feature.get("NAMELSAD10")

    try:
        geoid = feature.get("GEOID")
    except OGRIndexError:
        geoid = feature.get("GEOID10")

    state_abbrev = state_fips[fips_code].upper()
    name = name.encode("utf8").decode("latin-1")
    resp = u"{0} {1} {2}".format(state_abbrev, name, geoid)
    return resp


def geoid_tiger_namer(feature):
    try:
        geoid = feature.get("GEOID")
    except OGRIndexError:
        geoid = feature.get("GEOID10")
    return geoid


def nh_12_namer(feature):
    """
    New Hampshire's floterial district shapefiles have only one field:
    an abbreviated district name ("AA#" format). This has to be
    crosswalked to useful information.

    The crosswalk is roughly based on this Census file:
    www2.census.gov/geo/docs/maps-data/data/NH_2012_Floterials.txt
    """

    abbr = feature.get("NHHouse201")
    # There are two shapefiles that don't correspond to any floterial
    # These need unique IDs, which end with 'zzz' so that they'll be ignored
    if not abbr:
        import datetime

        unique_key = datetime.datetime.now()
        return "{}zzz".format(unique_key)

    path = os.path.join(
        os.path.abspath(os.getcwd()), "shapefiles", "nh_12_crosswalk.csv"
    )

    with open(path, "r") as f:
        # Due to a bug in `boundaries`, need to `import csv` here
        import csv

        reader = list(csv.DictReader(f))
        (row,) = [x for x in reader if x["NHHouse201"] == abbr]

        STATE_ABBREV = "NH"
        name = row["NAMELSAD"]
        geoid = row["GEOID"]

    resp = "{0} {1} {2}".format(STATE_ABBREV, name, geoid)
    return resp


def geoid_nh_12_namer(feature):
    abbr = feature.get("NHHouse201")
    if not abbr:
        import datetime

        unique_key = datetime.datetime.now()
        return "{}zzz".format(unique_key)

    path = os.path.join(
        os.path.abspath(os.getcwd()), "shapefiles", "nh_12_crosswalk.csv"
    )

    with open(path, "r") as f:
        # Due to a bug in `boundaries`, need to `import csv` here
        import csv

        reader = list(csv.DictReader(f))
        (row,) = [x for x in reader if x["NHHouse201"] == abbr]

        geoid = row["GEOID"]

    return geoid


class index_namer(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.count = 0

    def __call__(self, feature):
        self.count += 1
        return "{0}{1}".format(self.prefix, self.count)


CENSUS_URL = "http://www.census.gov/geo/maps-data/data/tiger.html"
LAST_UPDATE = date(2018, 1, 24)
defaults = dict(
    last_updated=LAST_UPDATE,
    domain="United States",
    authority="US Census Bureau",
    source_url=CENSUS_URL,
    license_URL=CENSUS_URL,
    data_url=CENSUS_URL,
    notes="",
    extra="{}",
)


FIRST_YEAR = 2017
LAST_YEAR = 2018
YEARS = range(FIRST_YEAR, LAST_YEAR + 1)
for year in YEARS:
    # Most types of Census data follow a common pattern
    for type_ in ["sldu", "sldl"]:
        boundary_info = dict(
            slug="{}-{}".format(type_, year % 2000),
            singular="{}-{}".format(type_, year % 2000),
            file="{}-{}/".format(type_, year % 2000),
            name_func=tiger_namer,
            id_func=geoid_tiger_namer,
            # Although the Census files are published in the autumn,
            # they take effect retroactively as of the start of their year
            start_date=date(year, 1, 1),
            end_date=date(year, 12, 31),
            encoding="latin-1",
            **defaults
        )
        if year == LAST_YEAR:
            # This is the most recent information we have,
            # so keep using it until the boundaries are updated
            del boundary_info["end_date"]
        boundaries.register(**boundary_info)


boundaries.register(
    "nh-12",
    singular="nh-12",
    file="nh-12/",
    name_func=nh_12_namer,
    id_func=geoid_nh_12_namer,
    start_date=date(2012, 1, 1),
    last_updated=LAST_UPDATE,
    domain="United States",
    authority="NH Office of Energy and Planning",
    source_url="http://www.nh.gov/oep/planning/services/gis/political-districts.htm",
    license_URL="http://www.nh.gov/oep/planning/services/gis/political-districts.htm",
    data_url="ftp://pubftp.nh.gov/OEP/NHHouseDists2012.zip",
    notes="",
    extra="{}",
)
