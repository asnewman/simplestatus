from rss_parser import Parser
from requests import get
import sqlite3
import email
import pytz
import datetime

con = sqlite3.connect("data.db")
cur = con.cursor()

rss_url = "https://www.redditstatus.com/history.rss"
xml = get(rss_url)

# Limit feed output to 5 items
# To disable limit simply do not provide the argument or use None
parser = Parser(xml=xml.content, limit=5)
feed = parser.parse()

# Iteratively print feed items
for item in feed.feed:
    timestamp = datetime.datetime.fromtimestamp( email.utils.mktime_tz(email.utils.parsedate_tz( item.publish_date )), pytz.utc ).timestamp()
    cur.execute(f"""
      INSERT INTO updates VALUES ("reddit", "{item.title}", "{item.description}", {timestamp}, "reddit.com", false)
    """)
    con.commit()      
    print(item.title)
    print(item.description)
    print(datetime.datetime.fromtimestamp( email.utils.mktime_tz(email.utils.parsedate_tz( item.publish_date )), pytz.utc ).timestamp())