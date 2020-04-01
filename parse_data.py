import os
import time
import pandas as pd
import numpy as np
import datetime
import argparse
import json
import requests
import math
from datetime import datetime
from dateutil import tz


def get_geocode(keyword, save_path):
    apikey = open("GEO_APIKEY", "r").read()
    url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(keyword+" California", apikey)
    r = requests.get(url)
    html = r.content.decode("utf-8")
    if save_path:
        dest_path = os.path.join(save_path, keyword.replace(" ", "_")+".json")
        with open(dest_path, "w") as f:
            f.write(html)
            print("{} saved".format(dest_path))
    data = json.loads(html)
    return data


def make_json(df, output_path=None):
    data = dict(type="FeatureCollection", features=[])
    for i in range(len(df)):
        row = df.iloc[i]
        timestamp = row["timestamp"].strftime("%m/%d/%Y %H:%M:%S")
        content = '<h3>{} <span class="badge badge-pill badge-warning">{}</span></h3>'.format(row["name"], int(row["crowdedness"]))
        if row["available"]:
            content += '<p><span class="badge badge-success"><b>In stock</b> </span> {}'.format(row["available"])
            if row["description"]:
                content += ' ({})'.format(row["description"])
            content += '</p>'
        if row["sold_out"]:
            content += '<p><span class="badge badge-danger"><b>Sold out</b> </span> {}'.format(row["sold_out"])
        if row["remark"]:
            content += '<p>{}</p>'.format(row["remark"])
        content += '<p class="text-sm-right"><i>submitted '
        if row["contributor"]:
            content += 'by: {} '.format(row["contributor"])
        content += 'at {}</i></p>'.format(timestamp)
        feature = dict(type="Feature", geometry=dict(type="Point", coordinates=[row["lng"], row["lat"]]),
                       properties=dict(name=row["name"], content=content))
        data["features"].append(feature)
    if output_path:
        with open(output_path, "w") as f:
            f.write(json.dumps(data))
    return data


def parse_data(df):
    df_markets = df.sort_values(by="timestamp", ascending=True).drop_duplicates(subset=["market", "city"], keep="last")
    data_new = list()
    count = 0
    for i in range(len(df_markets)):
        (market, city, crowdedness, available,
         description, sold_out, contributor, remark,
         timestamp) = df_markets.iloc[i][["market", "city", "crowdedness", "available", "description", "sold_out",
                                          "contributor", "remark", "timestamp"]]
        if city == "Online":
            continue
        if not (market and city):
            continue
        if isinstance(market, float) or isinstance(city, float):
            continue
        target = (market + " " + city).replace(" ", "_")
        target_path = os.path.join("data", target + ".json")
        if os.path.isfile(target_path):
            data = json.load(open(os.path.join("data", target + ".json")))
        else:
            data = get_geocode(market + " " + city, save_path="data")
            print(target, lat, lng)
        if len(data["results"]) < 1:
            continue
        lat = data["results"][0]["geometry"]["location"]["lat"]
        lng = data["results"][0]["geometry"]["location"]["lng"]
        # print(target, lat, lng)
        data_new.append([market + " " + city, lat, lng, crowdedness, available, description, sold_out, contributor,
                         remark, timestamp])
    df_new = pd.DataFrame(data_new, columns=["name", "lat", "lng", "crowdedness", "available", "description",
                                             "sold_out", "contributor", "remark", "timestamp"])
    return df_new


def main():
    csv_path = "data/out.csv"
    df = pd.read_csv(csv_path, index_col=0)
    df.loc[:, "timestamp"] = pd.to_datetime(df.loc[:, "timestamp"])
    df_new = parse_data(df)
    df_new.to_csv("data/export.csv")
    make_json(df_new, "data.json")


if __name__ == "__main__":
    main()
