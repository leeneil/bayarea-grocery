import os
import time
import pandas as pd
import datetime
import argparse
import requests
from datetime import datetime
from dateutil import tz
from bs4 import BeautifulSoup


def use_sample():
    html = open("data/sample.html", "r").read()
    return html


def get_html(url):
    r = requests.get(url)
    html = r.content.decode("utf-8")
    return html


def latest_update(ts):
    return ts.dropna().sort_values().iloc[-1]


def parse_html(html):
    data = list()
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all("table")
    trs = tables[1].tbody.find_all("tr")
    for i, tr in enumerate(trs):
        if i < 2:
            continue
        data.append([td.string for td in tr.find_all("td")])
    df = pd.DataFrame(data, columns=["market", "city", "date", "time", "zip", "available", "description", "sold_out",
                                     "crowdedness", "maskness", "contributor", "remark", "timestamp", "A", "B"])
    df.loc[:, "timestamp"] = df.loc[:, "timestamp"].apply(pd.to_datetime)
    df.loc[:, "timestamp"] = df.loc[:, "timestamp"].dt.tz_localize(tz.gettz("America/New York")).dt.tz_convert(tz.gettz("America/Los Angeles"))
    print("latest update: {}".format(latest_update(df["timestamp"])))
    return df


def get_data(url):
    html = get_html(url)
    df = parse_html(html)
    return df


def main():
    url = "https://docs.google.com/spreadsheets/d/1YpNdWWlvtZJ1xN7GW-XYMI_hEuU5u250bJUT55NM8Oc/htmlview?from=timeline&isappinstalled=0&fbclid=IwAR3kYiQoXmXACXP2dth3A77c1OvT1NHxTSLtO2RrTle3IGTy2-ibIhZ_VbY"
    df = get_data(url)
    df.to_csv("data/out.csv")


if __name__ == "__main__":
    main()
