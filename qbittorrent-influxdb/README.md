# qBittorrent-InfluxDB

This script collects your torrent info into InfluxDB so you can query and analyze it.

Requires `pip3 install influxdb`.

You should run this script with cron or systemd-timer. It's recommended to run at least once per minute.

Also provides a "GC" function to delete information for torrents that are no longer present in qBittorrent.
