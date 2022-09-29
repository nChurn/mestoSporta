from dadata import Dadata
from config import config


def get_data(addr):
    dadata = Dadata(config["DADATA_TOKEN"], config["DADATA_SECRET"])
    result = dadata.clean("address", addr)

    geo = result["geo_lat"] + " " + result["geo_lon"]
    metro = ""
    if result.get("metro"):
        metro = result["metro"][0]["name"] + " " + str(result["metro"][0]["distance"])
    return result["city_district"], geo, metro
