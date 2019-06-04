import argparse
from boxsdk.auth import OAuth2
import boxcrawler
import logging

logging.basicConfig(level=logging.WARNING)
DEV_TOKEN = ''
FOLDER = ''

def is_file_or_folder(item):
    return item.type in ['file','folder']

def has_shared_link(item):
    return item.shared_link is not None

# adds a task if the item has a shared link
def review_shared_link(item):
    if is_file_or_folder(item):
        if has_shared_link(item):
            logging.warning(item.response_object)
            task = item.create_task(f'Review {item.shared_link["access"]} Shared Link')
            task.assign(item.owned_by)

if __name__ == '__main__':
    auth = OAuth2(access_token=DEV_TOKEN, client_id=None, client_secret=None)
    fields = ['name','shared_link','owned_by']
    crawler = boxcrawler.BoxCrawler(auth)
    crawler.crawl(FOLDER, review_shared_link, fields=fields)

