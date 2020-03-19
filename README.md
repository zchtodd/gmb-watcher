# GMB Watcher

A simple browser automation tool for monitoring GMB listings.

This tool makes it convenient to automatically watch several GMB listings for updates.  The monitored listings
are stored in a SQLite database and periodically checked via the Puppeteer browser automation framework.

An email containing a screenshot is sent to a specified recipient whenever updates are detected on a GMB listing.

This tool requires a proxy provider and a Mailgun API key.

[Instructions for getting started with this tool.](https://persuaded.io/blog/building-a-gmb-listing-watcher/)
