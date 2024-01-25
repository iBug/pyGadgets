#!/usr/bin/python3

import datetime
import influxdb
import json
import os
import requests
import sys
from http.cookiejar import http2time


os.chdir(os.path.dirname(os.path.realpath(__file__)))
with open("config.json", "r") as f:
    config = json.load(f)
    client = influxdb.InfluxDBClient(**config["influxdb"])


def get_data():
    url = config["qbittorrent"]["url"] + "/api/v2/torrents/info"
    resp = requests.get(url)
    time = datetime.datetime.utcfromtimestamp(http2time(resp.headers["Date"]))
    return resp.json(), time


def make_points(data, time: datetime.datetime):
    timestamp = time.timestamp()
    time_s = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    return [{
        "measurement": "qbittorrent",
        "time": time_s,
        "tags": {
            "name": item["name"],
            "hash": item["hash"],
            "category": item["category"],
        },
        "fields": {
            "added_on": int(timestamp - item["added_on"]),
            "size": item["size"],
            "last_activity": int(timestamp - item["last_activity"]),
            "seen_complete": int(timestamp - item["seen_complete"]),
            "ratio": float(item["ratio"]),
            "downloaded": item["downloaded"],
            "uploaded": item["uploaded"],
        },
    } for item in data]


def upload_points(points):
    client.write_points(points)


def collect():
    data, time = get_data()
    points = make_points(data, time)
    upload_points(points)


def gc():
    data, time = get_data()
    time_s = time.strftime("%Y-%m-%d %H:%M:%S")
    qb_hashes = {item["hash"]: item["name"] for item in data}
    db = client.query('SHOW TAG VALUES FROM "qbittorrent" WITH KEY = "hash"')
    db_hashes = {item["value"] for item in db.get_points()}
    for hash in db_hashes - set(qb_hashes):
        print("[{}] Removing {} ({})".format(time_s, hash, qb_hashes[hash]))
        client.query("""DROP SERIES FROM "qbittorrent" WHERE "hash" = '{}'""".format(hash))


def main():
    action = "collect"
    if len(sys.argv) > 1:
        action = sys.argv[1]

    if action == "collect":
        collect()
    elif action == "gc":
        gc()


if __name__ == "__main__":
    main()
