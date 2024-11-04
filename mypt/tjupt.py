#!/usr/bin/python3

import qbittorrentapi

from util import now_ts, chdir, load_config, delete_torrent


def hnr_time(size: int) -> int:
    day = 86400
    gib = 2 ** 30
    for i in range(1, 6):
        if size <= i * 10 * gib:
            return i * day
    return 7 * day


def main():
    chdir()
    config = load_config()
    qb = qbittorrentapi.Client(host=config["qbittorrent"]["url"])
    qb.auth_log_in()
    delete_count = 0
    for torrent in qb.torrents_info(category="Auto", tag="TJUPT"):
        if 0 < torrent.progress < 1:
            # Incomplete torrent
            continue
        hr = hnr_time(torrent.size)
        last_active = now_ts - torrent.last_activity
        seeding_time = now_ts - torrent.completion_on
        added_ago = now_ts - torrent.added_on
        if last_active > hr * 1.2:
            torrent.reannounce()
            delete_torrent(torrent)
            delete_count += 1
        elif seeding_time < added_ago and seeding_time > hr * 3.0:
            torrent.reannounce()
            delete_torrent(torrent)
            delete_count += 1
    if delete_count:
        print(f"Deleted {delete_count} torrents from qBittorrent")


if __name__ == "__main__":
    main()
