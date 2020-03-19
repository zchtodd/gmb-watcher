import os
import sqlite3
import subprocess
import base64
import requests
import logging
import json
import time


UPDATE_INTERVAL = 60
SCRAPE_TIMEOUT = 25
UPDATES_RECIPIENT = "zchtodd@gmail.com"
MAILGUN_API_KEY = os.environ["MAILGUN_API_KEY"]

LISTING_SCHEMA = """
    CREATE TABLE listing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        url TEXT,
        last_checked DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def send_notification(listing, image_data):
    with open("gmb.png", "wb") as f:
        f.write(base64.b64decode(image_data))

    return requests.post(
        "https://api.mailgun.net/v3/www.persuaded.io/messages",
        auth=("api", MAILGUN_API_KEY),
        files=[("inline", open("gmb.png", "rb"))],
        data={
            "from": "GMB Watcher <zchtodd@persuaded.io>",
            "to": UPDATES_RECIPIENT,
            "subject": "GMB Update for {}".format(listing["name"]),
            "html": '<html><img src="cid:gmb.png"></html>',
        },
    )


def check_listing(listing):
    p = subprocess.run(
        'node check.js "{}" "{}"'.format(listing["name"], listing["url"]),
        shell=True,
        capture_output=True,
        timeout=SCRAPE_TIMEOUT,
    )

    data = json.loads(p.stdout.decode("utf-8"))
    if data["data"]:
        send_notification(listing, data["data"])
    return data


def watch():
    while True:
        conn = sqlite3.connect("gmbwatch.db3")
        conn.row_factory = dict_factory

        c = conn.cursor()

        c.execute(
            (
                "SELECT listing.*, "
                "(strftime('%s', datetime('now')) - strftime('%s', last_checked)) AS elapsed "
                "FROM listing WHERE elapsed > ? LIMIT 1"
            ),
            (UPDATE_INTERVAL,),
        )

        listing = c.fetchone()

        if listing:
            try:
                data = check_listing(listing)
            except (subprocess.TimeoutExpired, json.decoder.JSONDecodeError) as err:
                logging.warning(str(err))
                continue

            c.execute(
                "UPDATE listing SET name = ?, last_checked = datetime('now') WHERE id = ?",
                (data["name"], listing["id"]),
            )

            conn.commit()

        conn.close()
        time.sleep(1)


if __name__ == "__main__":
    if not os.path.exists("gmbwatch.db3"):
        conn = sqlite3.connect("gmbwatch.db3")
        c = conn.cursor()

        c.execute(LISTING_SCHEMA)
        conn.commit()
        conn.close()

    watch()
