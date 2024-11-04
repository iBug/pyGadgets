#!/usr/bin/python3

import json
import os
import qbittorrentapi
import random
import re
import requests

from bs4 import BeautifulSoup

from util import now_ts, chdir, load_config, format_status, delete_torrent

chdir()
config = load_config()
with open("data.json", "r") as f:
    data = json.load(f)
    seen = []
    chance = 1
    for id in data.get("seen", []):
        chance *= 0.99
        if chance > random.random():
            seen.append(id)
    data["seen"] = seen


day = 86400
GB = 1 << 30
qb = qbittorrentapi.Client(host=config["qbittorrent"]["url"])

for torrent in qb.torrents_info():
    if torrent.category != "Auto":
        continue
    tags = torrent.tags.split(",")
    if any([x in tags for x in ["Keep", "TJUPT"]]):
        continue

    last_active_ago = now_ts - torrent.last_activity
    added_ago = now_ts - torrent.added_on
    deleted = False
    for active_days, target_GB, target_ratio in [
        (14, 1024, 20.0),
        (7, 600, 15.0),
        (3, 250, 12.0),
        (1, 100, 10.0),
    ]:
        if last_active_ago > active_days * day:
            if torrent.uploaded < target_GB * GB and torrent.ratio < target_ratio:
                delete_torrent(torrent)
                deleted = True
                break
            if torrent.save_path == "/mnt/bts":
                print(f"Move {format_status(torrent)}")
                torrent.set_save_path("/mnt/bt1")
                break
    if deleted:
        continue

    if last_active_ago < 6 * 3600:
        # Skip added_days-based check if active within 6h
        continue
    for added_days, target_GB, target_ratio in [
        (30, 1024, 15.0),
        (14, 500, 15.0),
        (7, 300, 12.0),
        (3, 200, 10.0),
        (1, 100, 5.0),
        (0.5, 50, 1.0),
    ]:
        if added_ago > added_days * day:
            if torrent.uploaded < target_GB * GB and torrent.ratio < target_ratio:
                delete_torrent(torrent)
            break


headers = {
    "User-Agent": config["byr"]["user-agent"],
    "Cookie": config["byr"]["cookie"],
}

resp = requests.get("https://byr.pt/torrents.php", headers=headers)
resp.raise_for_status()
if resp.history:
    print("login failed, try again")
    # import decaptcha
    # d = decaptcha.DeCaptcha()
    # d.load_model("captcha_classifier.pkl")

    payload = {
        "username": config["byr"]["username"],
        "password": config["byr"]["password"],
        "autologin": "yes",
    }
    resp = requests.post("https://byr.pt/takelogin.php", data=payload, headers=headers | {
        "Origin": "https://byr.pt",
        "Referer": "https://byr.pt/login.php",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    if not resp.history:
        os.exit(1)
    resp.raise_for_status()
    config["byr"]["cookie"] = resp.history[0].headers["Set-Cookie"].split(" ", 1)[0]
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

soup = BeautifulSoup(resp.text, "lxml")
links = soup.select("tr.free_bg a[href^='details.php?']") + soup.select("tr.twoupfree_bg a[href^='details.php?']")
ids = set()
for link in links:
    id = re.search(r"id=(\d+)", link.attrs["href"])[1]
    ids.add(id)
    if len(ids) >= 20:
        break
ids = [id for id in ids if id not in seen]
urls = [f"https://byr.pt/download.php?id={id}&passkey={config["byr"]['passkey']}" for id in ids]
qb.torrents_add(urls=urls, category="Auto")
with open("data.json", "w") as f:
    seen.extend(ids)
    json.dump(data, f, indent=2, ensure_ascii=False)
