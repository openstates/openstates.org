#!/usr/bin/env python

import os
import glob

import us

states = [s for s in us.STATES_AND_TERRITORIES if s not in us.OBSOLETE]
fips = sorted([s.fips for s in states])


def _download_file(URL, where):
    # create directory and work in it
    pop = os.path.abspath(os.getcwd())
    if not os.path.exists(where):
        os.makedirs(where)
    os.chdir(where)

    fname = os.path.basename(URL)
    if not os.path.exists(fname):
        os.system("wget %s" % (URL))

    os.chdir(pop)


def _list_files(*flags):
    files = os.listdir(".")
    for _file in files:
        for flag in flags:
            if _file.endswith(flag):
                yield _file


def _extract_cwd(path=None):
    pop = os.path.abspath(os.getcwd())
    if path:
        os.chdir(path)
    dirname = os.path.basename(os.getcwd())

    for f in glob.glob("*.zip"):
        os.system("unzip -o %s" % f)

    for path in _list_files("dbf", "prj", "shp", "xml", "shx"):
        os.renames(path, "../../shapefiles/{dirname}/{path}".format(**locals()))

    os.chdir(pop)


def _download_census_file(top, fips, what, year, where):

    if year == "13":
        URL = (
            "https://www2.census.gov/geo/tiger/{top}/{fips}/tl_rd{year}_{fips}_{what}.zip"
        ).format(**{"year": year, "what": what, "fips": fips, "top": top})
    else:
        URL = (
            "https://www2.census.gov/geo/tiger/{top}/{WHAT}/tl_{year}_{fips}_{what}.zip"
        ).format(
            **{
                "year": year,
                "what": what,
                "WHAT": what.upper(),
                "fips": fips,
                "top": top,
            }
        )

    _download_file(URL, where)


def download_state_leg_bounds():
    for fip in fips:
        _download_census_file("TIGER2018", fip, "sldl", "2018", "downloads/sldl-18")
        _download_census_file("TIGER2018", fip, "sldu", "2018", "downloads/sldu-18")

        _download_census_file("TIGER2017", fip, "sldl", "2017", "downloads/sldl-17")
        _download_census_file("TIGER2017", fip, "sldu", "2017", "downloads/sldu-17")

        # _download_census_file("TIGER2016", fip, "sldl", "2016", "downloads/sldl-16")
        # _download_census_file("TIGER2016", fip, "sldu", "2016", "downloads/sldu-16")

        # _download_census_file("TIGER2015", fip, "sldl", "2015", "downloads/sldl-15")
        # _download_census_file("TIGER2015", fip, "sldu", "2015", "downloads/sldu-15")

        # _download_census_file("TIGER2014", fip, "sldl", "2014", "downloads/sldl-14")
        # _download_census_file("TIGER2014", fip, "sldu", "2014", "downloads/sldu-14")

        # _download_census_file("TIGERrd13_st", fip, "sldl", "13", "downloads/sldl-13")
        # _download_census_file("TIGERrd13_st", fip, "sldu", "13", "downloads/sldu-13")

        # _download_census_file("TIGER2012", fip, "sldl", "2012", "downloads/sldl-12")
        # _download_census_file("TIGER2012", fip, "sldu", "2012", "downloads/sldu-12")

    for x in [
        "downloads/sldl-18",
        "downloads/sldu-18",
        "downloads/sldl-17",
        "downloads/sldu-17",
        # "downloads/sldl-16", "downloads/sldu-16",
        # "downloads/sldl-15", "downloads/sldu-15",
        # "downloads/sldl-14", "downloads/sldu-14",
        # "downloads/sldl-13", "downloads/sldu-13",
        # "downloads/sldl-12", "downloads/sldu-12"
    ]:
        _extract_cwd(x)


def download_counties():
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGER2017/COUNTY/tl_2017_us_county.zip",
        "downloads/county-17",
    )
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGER2016/COUNTY/tl_2016_us_county.zip",
        "downloads/county-16",
    )
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGER2015/COUNTY/tl_2015_us_county.zip",
        "downloads/county-15",
    )
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGER2014/COUNTY/tl_2014_us_county.zip",
        "downloads/county-14",
    )

    for fip in fips:
        _download_census_file(
            "TIGERrd13_st", fip, "county10", "13", "downloads/county-13"
        )

    for x in [
        "downloads/county-17",
        "downloads/county-16",
        "downloads/county-15",
        "downloads/county-14",
        "downloads/county-13",
    ]:
        _extract_cwd(x)


def download_places():
    for fip in fips:
        _download_census_file("TIGER2017", fip, "place", "2017", "downloads/place-17")
        _download_census_file("TIGER2016", fip, "place", "2016", "downloads/place-16")
        _download_census_file("TIGER2015", fip, "place", "2015", "downloads/place-15")
        _download_census_file("TIGER2014", fip, "place", "2014", "downloads/place-14")
        _download_census_file(
            "TIGERrd13_st", fip, "place10", "13", "downloads/place-13"
        )

    for x in [
        "downloads/place-17",
        "downloads/place-16",
        "downloads/place-15",
        "downloads/place-14",
        "downloads/place-13",
    ]:
        _extract_cwd(x)


def download_nh_floterial():
    # New Hampshire has a second set of boundaries, that aren't served by the Census
    # Hosted here: https://www.nh.gov/oep/planning/services/gis/political-districts.htm
    _download_file("ftp://pubftp.nh.gov/OEP/NHHouseDists2012.zip", "downloads/nh-12")

    # Only want the floterial file, not the main district file
    pop = os.path.abspath(os.getcwd())
    os.chdir("downloads/nh-12")
    dirname = os.path.basename(os.getcwd())

    for f in glob.glob("*.zip"):
        os.system("unzip -o %s" % f)

    for path in _list_files("dbf", "prj", "shp", "xml", "shx"):
        if "NHHouse2012Float" in path:
            os.renames(path, "../../shapefiles/{dirname}/{path}".format(**locals()))

    os.chdir(pop)


def download_cds():
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGER2017/CD/tl_2017_us_cd115.zip",
        "downloads/cd-115",
    )
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGER2015/CD/tl_2015_us_cd114.zip",
        "downloads/cd-114",
    )

    for fip in fips:
        _download_census_file("TIGERrd13_st", fip, "cd113", "13", "downloads/cd-113")
        _download_census_file("TIGERrd13_st", fip, "cd111", "13", "downloads/cd-111")

    for x in [
        "downloads/cd-115",
        "downloads/cd-114",
        "downloads/cd-113",
        "downloads/cd-111",
    ]:
        _extract_cwd(x)


def download_zcta():
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGER2017/ZCTA5/tl_2017_us_zcta510.zip",
        "downloads/zcta-17",
    )
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGER2016/ZCTA5/tl_2016_us_zcta510.zip",
        "downloads/zcta-16",
    )
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGER2015/ZCTA5/tl_2015_us_zcta510.zip",
        "downloads/zcta-15",
    )
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGER2014/ZCTA5/tl_2014_us_zcta510.zip",
        "downloads/zcta-14",
    )
    _download_file(
        "https://www2.census.gov/geo/tiger/TIGERrd13_st/nation/tl_rd13_us_zcta510.zip",
        "downloads/zcta-13",
    )

    for x in [
        "downloads/zcta-17",
        "downloads/zcta-16",
        "downloads/zcta-15",
        "downloads/zcta-14",
        "downloads/zcta-13",
    ]:
        _extract_cwd(x)


if __name__ == "__main__":
    download_nh_floterial()
    # download_counties()
    # download_places()
    # download_cds()
    download_state_leg_bounds()
    # download_zcta()
