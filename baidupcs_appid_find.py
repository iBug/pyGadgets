#!/usr/bin/env python3

import sys
import os
import os.path as path
import time
import requests
import json
import argparse


HOST = "http://pcs.baidu.com"
PATH = "/rest/2.0/pcs/file"
headers = {
    # Need to set Cookie BDUSS first
    'User-Agent': "netdisk;1.0",
}
throttle = 0


def check_appid(appid):
    params = {
        'app_id': str(appid),
        'method': "list",
        'path': "/",
    }
    response = requests.get(HOST + PATH, params=params, headers=headers)
    return response.status_code == 200


def load_bduss():
    with open(path.join(path.expanduser("~"), ".config", "BaiduPCS-Go", "pcs_config.json")) as f:
        pcs_config = json.load(f)
    try:
        return pcs_config["baidu_user_list"][0]["bduss"]
    except (ValueError, KeyError):
        return None


def parse_args():
    parser = argparse.ArgumentParser(description="Baidu PCS AppID searcher")
    parser.add_argument("start", help="Start of search range", type=int)
    parser.add_argument("end", help="End of search rande (exclusive)", type=int)

    parser.add_argument("-i", "--interval", help="Time interval between requests", type=float, default=0.0)
    parser.add_argument("--bduss", help="Use the given BDUSS", type=float, default=0.0)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    bduss = args.bduss or load_bduss()
    if not bduss:
        print("No BDUSS found in PCS config!", file=sys.stderr)
        os._exit(1)
    # print("Found BDUSS from config: {}".format(bduss))
    headers['Cookie'] = "BDUSS={}".format(bduss)
    for aid in range(266700, 266720):
        print("\rChecking {}".format(aid), end='')
        if check_appid(aid):
            print("\rAvailable AppID found: {}".format(aid))
        time.sleep(args.interval)
