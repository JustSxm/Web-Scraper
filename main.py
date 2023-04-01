import configparser
import time
from multiprocessing import Process

from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from utils import print_info
from websites.ebay.ebay import Ebay
from websites.facebook.facebook import Facebook
from websites.kijiji.kijiji import Kijiji


def main(config):
    print_info("Activating Scraper...")
    interval = config["DEFAULT"].getint("Interval")
    while True:
        if(config['FACEBOOK']['Enabled'] == 'True'):
            p = Process(target=create_process, args=(Facebook, config))
            p.start()
            p.join()
        if(config['KIJIJI']['Enabled'] == 'True'):
            p = Process(target=create_process, args=(Kijiji, config))
            p.start()
            p.join()
        if(config['EBAY']['Enabled'] == 'True'):
            p = Process(target=create_process, args=(Ebay, config))
            p.start()
            p.join()
        time.sleep(60 * interval)

def create_process(classToCall, config):
    process = CrawlerProcess(settings={"FEEDS": {"items.json": {"format": "json", "overwrite": False}, }, "USER_AGENT": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36)', "LOG_ENABLED": False})
    if classToCall == Facebook:
        process = CrawlerProcess(settings={"FEEDS": {"items.json": {"format": "json"},},"LOG_ENABLED": False})
    
    process.crawl(classToCall, config)
    process.start()
    return process

if __name__ == "__main__":
    print_info("Starting scraper")
    config = configparser.ConfigParser()
    config.read('config.ini')
    main(config)


        
