from dotenv import load_dotenv
load_dotenv()

import sqlite3
import requests
import feedparser
import os

slack_webhook = os.environ.get('SLACK_WEBHOOK')

def update_rss_feeds(feeds):
    conn = sqlite3.connect('feeds.db')
    c = conn.cursor()

    # Create entries table if it does not exist
    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY,
            title TEXT,
            link TEXT,
            pub_date TEXT,
            feed_name TEXT,
            feed_url TEXT
        )
    """)

    for name, url in feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            pub_date = entry.published

            # Check if entry already exists in the database
            c.execute("SELECT * FROM entries WHERE title=? AND link=?", (title, link))
            existing_entry = c.fetchone()

            if existing_entry is None:
                # Entry does not exist, insert into database
                c.execute("INSERT INTO entries (title, link, pub_date, feed_name, feed_url) VALUES (?, ?, ?, ?, ?)", (title, link, pub_date, name, url))
                print(f"New entry added to {name} feed: {title}")
                send_slack_message(slack_webhook, f"Issue with {name}: {title} {link}")

    # Commit changes to the database and close the connection
    conn.commit()
    conn.close()

def send_slack_message(webhook_url, message):
    """
    Sends a message to a Slack channel using a webhook URL.

    Args:
        webhook_url (str): The webhook URL for the Slack channel.
        message (str): The message to send.

    Returns:
        None.
    """
    # Create the payload
    payload = {
        "text": message
    }

    # Send the request to the Slack API
    response = requests.post(webhook_url, json=payload)

    # Check the response status code
    if response.status_code != 200:
        raise ValueError("Request to Slack API failed: {}".format(response.text))


rss_feeds = {
    "github": "https://www.githubstatus.com/history.rss",
    "figma": "https://status.figma.com/history.rss",
    "slack": "https://status.slack.com/feed/rss",
    "datadog": "https://status.datadoghq.com/history.rss",
    "fullstory": "https://status.fullstory.com/history.rss",
    "sentry": "https://status.sentry.io/history.rss"
}

db_file = "feeds.db"

update_rss_feeds(rss_feeds)
