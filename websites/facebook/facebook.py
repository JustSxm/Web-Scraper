from cmath import e
import json
import scrapy

from Ad import Ad
from utils import print_info, print_scraper


class Facebook(scrapy.Spider):
    name = "facebook"

    def __init__(self, config, **kwargs):
        print_scraper("FACEBOOK", "Starting...")
        city_id = config["FACEBOOK"]["CityId"]
        min_price = config["FACEBOOK"]["MinPrice"]
        max_price = config["FACEBOOK"]["MaxPrice"]
        sort_by = config["FACEBOOK"]["SortBy"]
        keywords = '%20'.join(config["DEFAULT"]["Keywords"].split(" "))
        self.keywords = config["DEFAULT"]["Keywords"].split(" ")
        self.exclusions = config["DEFAULT"]["Exclusions"].split(" ")
        self.strictmode = config["DEFAULT"].getboolean("StrictMode")
        self.start_urls = ["https://www.facebook.com/marketplace/" + city_id + "/search?minPrice=" + min_price +
                           "&maxPrice=" + max_price + "&daysSinceListed=10" + "&sortBy=" + sort_by + "&query=" + keywords]
        print_scraper("FACEBOOK", "Started !")
        super().__init__(**kwargs)

    def parse(self, response):
        print_scraper("FACEBOOK", "Scraping...")
        allAds = []
        
        # get all the script elements
        flex_selector = response.xpath('//*[@id="facebook"]/body/script/text()')
        
        ads = []
        # try to find the right one
        for script in flex_selector.getall():
            try:
                ads = json.loads(script)
                ads = ads['require'][0][3][0]['__bbox']['require'][0][3][1]['__bbox']['result']['data']['marketplace_search']['feed_units']['edges']
                break
            except:
                pass
        if(len(ads) == 0):
            print_scraper("FACEBOOK", "No results found")
            return None
        print_scraper("FACEBOOK", "Found ads")

        # parse each json
        for adJson in ads:
            try:
                title = adJson['node']['listing']['marketplace_listing_title']

                # Skip if title contains any of the exclusion keywords
                if any(exclusions.lower() in title.lower() for exclusions in self.exclusions):
                    continue

                # Skip if title does not contain any of the keywords (if strict mode is enabled)
                if self.strictmode and not any(x.lower() in title.lower() for x in self.keywords) :
                    continue
                    
                ad = Ad()
                ad["title"] = title
                ad["price"] = adJson['node']['listing']['listing_price']['amount']
                ad["link"] = 'https://www.facebook.com/marketplace/item/' + adJson['node']['listing']['id']
                print_scraper("FACEBOOK", "An ad fitting the criterias was found")
                allAds.append(ad)
            except:
                pass
        return allAds
