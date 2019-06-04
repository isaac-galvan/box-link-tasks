import logging
import threading
import queue
import time

from boxsdk import Client

class BoxCrawler(object):
    def __init__(self, auth, workers=5, wait = 0.5):
        self.auth = auth
        self.num_workers = workers
        self.wait = wait
        self.folders_queue = queue.Queue()

    def crawl(self, folder_id, callback, fields=['name']):
        self.fields = fields
        self.func = callback
        self.folders_queue.put(folder_id)

        # start the threads
        threads = list()
        for i in range(self.num_workers):
            t = threading.Thread(target=self.worker)
            t.start()
            threads.append(t)

        # block until the input queue is empty
        self.folders_queue.join()
        for i in range(self.num_workers):
            self.folders_queue.put(None)

        # block until the workers finish their jobs
        for t in threads:
            t.join()

        return None

    def worker(self):
        while True:
            folder_id = self.folders_queue.get()
            if folder_id is None:
                break

            logging.info(f'getting items for {folder_id}')
            client = Client(self.auth)
            
            # store folder items in list as generator can be interated once
            current_folder_items = list(client.folder(folder_id=folder_id).get_items(fields=self.fields))

            # add the subfolders to the queue
            subfolders = filter(lambda f: f.type =='folder', current_folder_items)
            for s in subfolders:
                self.folders_queue.put(s.id)           

            # run the callback on each folder item
            for item in current_folder_items:
                self.func(item)

            # pause to keep API calls in check
            time.sleep(self.wait)
            self.folders_queue.task_done()