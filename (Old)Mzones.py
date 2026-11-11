import sys
print(sys.executable)

import geopandas as gpd
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

uhfDis = gpd.read_file(BASE_DIR/"UHF42.geo.json").to_crs(epsg=2263)
# zones = gpd.read_file(BASE_DIR/"zones.json").to_crs(epsg=2263)

shapefile_path = BASE_DIR / "nyzd.shp"

zones = gpd.read_file(shapefile_path).to_crs(epsg=2263)

uhfDis["total_zone_sqft"] = uhfDis.geometry.area

# is_m = zones["ZONEDIST"].str.match(r"^M[1-3]")
is_m = zones["ZONEDIST"].str.match(r"^M3")
is_mixed = zones["ZONEDIST"].str.contains("/") | zones["ZONEDIST"].str.contains("MX")
pure_m = zones[is_m & ~is_mixed].copy()

# print(pure_m)

pure_m_dissolved = pure_m.dissolve()

intersection = gpd.overlay(uhfDis, pure_m_dissolved, how="intersection")

intersection["m_sqft"] = intersection.geometry.area

uhf_col = "GEOCODE" if "GEOCODE" in intersection.columns else "id"
m_totals = intersection.groupby(uhf_col)["m_sqft"].sum().reset_index()

result = uhfDis.merge(m_totals, on=uhf_col, how="left")
result["m_sqft"] = result["m_sqft"].fillna(0)
result["percent_m_zone"] = (result["m_sqft"] / result["total_zone_sqft"]) * 100

def printAll():
    output_cols = [uhf_col, "GEONAME", "BOROUGH", "AsthmaRate", "total_zone_sqft", "m_sqft", "percent_m_zone"]
    final_table = result[[c for c in output_cols if c in result.columns]].sort_values(
        by="percent_m_zone", ascending=False
    )
    print(final_table)

def printMain():
    output_cols = ["GEONAME", "BOROUGH", "AsthmaRate", "percent_m_zone"]
    final_table = result[[c for c in output_cols if c in result.columns]].sort_values(
        by="percent_m_zone", ascending=False
    )
    print(final_table)

printAll()
# printMain()


# for line in uhfDis:
#     gpd.overlay(line, )

# print(uhfDis)