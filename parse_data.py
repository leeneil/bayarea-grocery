import os
import time
import pandas as pd
import numpy as np
import datetime
import argparse
import json
import requests
import math


def get_geocode(keyword, save_path):
    apikey = open("APIKEY", "r").read()
    url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(keyword, apikey)
    r = requests.get(url)
    html = r.content.decode("utf-8")
    if save_path:
        with open(os.path.join(save_path, keyword.replace(" ", "_")+".json"), "w") as f:
            f.write(html)
    data = json.loads(html)
    return data


def make_json(df, output_path):
    data = dict(type="FeatureCollection", features=[])
    for i in range(len(df)):
        row = df.iloc[i]
        content = '<h3>{}</h3>'.format(row["name"])
        if str(row["available"]) != "nan":
            content += '<p><b>In stock: </b>{}'.format(row["available"])
            if str(row["description"]) != "nan":
                content += ' ({})'.format(row["description"])
            content += '</p>'
        if str(row["sold_out"]) != "nan":
            content += '<p><b>Sold out: </b>{}</p>'.format(row["sold_out"])
        content += '<p><i>submitted '
        if str(row["contributor"]) != "nan":
            content += 'by: {} '.format(row["contributor"])
        content += 'at {}</i></p>'.format(row["timestamp"])
        feature = dict(type="Feature", geometry=dict(type="Point", coordinates=[row["lng"], row["lat"]]),
                       properties=dict(name=row["name"], content=content))
        data["features"].append(feature)
    with open(output_path, "w") as f:
        f.write(json.dumps(data))


def main():
    df = pd.read_csv("data/out.csv", index_col=0)
    df_markets = df.sort_values(by="timestamp", ascending=True).drop_duplicates(subset=["market", "city"], keep="last")
    data_new = list()
    print(df_markets)
    count = 0
    for i in range(len(df_markets)):
        (market, city, crowdedness, available, description,
         sold_out, contributor, timestamp) = df_markets.iloc[i][["market",  "city", "crowdedness", "available",
                                                                 "description",  "sold_out", "contributor", "timestamp"]]
        if city == "Online":
            continue
        print(market, city)
        target = (market+" "+city).replace(" ", "_")
        if os.path.isfile(os.path.join("data", target+".json")):
            data = json.load(open(os.path.join("data", target+".json")))
        else:
            data = get_geocode(market+" "+city+" California", save_path="data")
        if len(data["results"]) < 1:
            continue
        lat = data["results"][0]["geometry"]["location"]["lat"]
        lng = data["results"][0]["geometry"]["location"]["lng"]
        print(target, lat, lng)
        data_new.append([market+" "+city, lat, lng, crowdedness, available, description, sold_out, contributor,
                         timestamp])
    df_new = pd.DataFrame(data_new, columns=["name", "lat", "lng", "crowdedness", "available", "description",
                                             "sold_out", "contributor", "timestamp"])
    df_new.to_csv("data/export.csv")

    make_json(df_new, "data.json")


if __name__ == "__main__":
    main()
