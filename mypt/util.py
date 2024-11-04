import datetime
import humanize
import json
import os
import qbittorrentapi


now = datetime.datetime.now()
now_s = now.strftime("%Y-%m-%d %H:%M:%S")
now_ts = int(now.timestamp())


def chdir() -> None:
    cwd = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cwd)


def load_config(filename: str = "config.json") -> dict:
    with open(filename, "r") as f:
        return json.load(f)


def format_size(n: int) -> str:
    return humanize.naturalsize(n, binary=True)


def format_duration(n: int) -> str:
    if n < 60:
        return f"{n}s"
    if n < 3600:
        return f"{n // 60}m{n % 60}s"
    if n < 86400:
        return f"{n // 3600}h{n % 3600 // 60}m"
    return f"{n // 86400}d{n % 86400 // 3600}h"


def format_status(torrent: qbittorrentapi.TorrentDictionary) -> str:
    last_active_ago = now_ts - torrent.last_activity
    added_ago = now_ts - torrent.added_on
    return (
        f"{torrent.name} ({format_size(torrent.size)}, "
        f"up {format_size(torrent.uploaded)} / {torrent.ratio:.2f}, "
        f"added {format_duration(added_ago)}, "
        f"last active {format_duration(last_active_ago)})"
    )


def delete_torrent(torrent: qbittorrentapi.TorrentDictionary) -> None:
    print(f"Delete {format_status(torrent)}")
    torrent.delete(delete_files=True)
