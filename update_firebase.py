import time
import pyrebase
from datetime import datetime
from get_data import get_data
from parse_data import parse_data, make_json


def get_and_parse():
    url = "https://docs.google.com/spreadsheets/d/1YpNdWWlvtZJ1xN7GW-XYMI_hEuU5u250bJUT55NM8Oc/htmlview?from=timeline&isappinstalled=0&fbclid=IwAR3kYiQoXmXACXP2dth3A77c1OvT1NHxTSLtO2RrTle3IGTy2-ibIhZ_VbY"
    df = get_data(url)
    df_new = parse_data(df)
    geojson = make_json(df_new)
    return geojson


def main():
    config = {
      "apiKey": "{}".format(open("FIREBASE_APIKEY", "r").read()),
      "authDomain": "bayarea-grocery.firebaseapp.com",
      "databaseURL": "https://bayarea-grocery.firebaseio.com",
      "storageBucket": "grocery.appspot.com",
      "serviceAccount": "bayarea-grocery-b206dae88354.json"
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    t1 = -1
    while True:
        if time.time() - t1 < 60*15:
            pass
        else:
            t1 = time.time()
            timestamp = datetime.now()
            print(timestamp)
            data = get_and_parse()
            db.child("geojson").set(data)
            print("success")


if __name__ == "__main__":
    main()