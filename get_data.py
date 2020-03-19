import os
import time
import pandas as pd
import datetime
import argparse
import requests
from bs4 import BeautifulSoup


def use_sample():
    html = open("data/sample.html", "r").read()
    return html


def get_html(url):
    r = requests.get(url)
    html = r.content.decode("utf-8")
    return html


def parse_html(html):
    data = list()
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all("table")
    trs = tables[0].tbody.find_all("tr")
    for i, tr in enumerate(trs):
        if i < 2:
            continue
        data.append([td.string for td in tr.find_all("td")])
    df = pd.DataFrame(data, columns=["market", "city", "date", "time", "zip", "available", "description", "sold_out",
                                     "crowdedness", "maskness", "contributor", "memark", "timestamp", "A", "B"])
    return df


def main():
    url = "https://docs.google.com/spreadsheets/d/1YpNdWWlvtZJ1xN7GW-XYMI_hEuU5u250bJUT55NM8Oc/htmlview?from=timeline&isappinstalled=0&fbclid=IwAR3kYiQoXmXACXP2dth3A77c1OvT1NHxTSLtO2RrTle3IGTy2-ibIhZ_VbY"
    html = get_html(url)
    # html = use_sample()
    df = parse_html(html)
    df.to_csv("data/out.csv")


if __name__ == "__main__":
    main()
