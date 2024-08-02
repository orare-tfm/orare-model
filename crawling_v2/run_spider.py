import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Import your spiders from crawling.py
from crawling_v2.spiders.crawling import CrawlingSpider1, CrawlingSpider2, CrawlingSpider3, CrawlingSpider4

def run_spiders():
    # Get the project settings
    settings = get_project_settings()

    # Set output format and file paths for each spider
    settings.set('FEED_FORMAT', 'json')
    settings.set('FEED_URI', 'data/postal_codes_v2.json', priority='cmdline')
    
    # Create a CrawlerProcess with the project settings
    process = CrawlerProcess(settings)

    # Add each spider to the process by their class
    process.crawl(CrawlingSpider4)

    # Start the crawling process
    process.start()

if __name__ == '__main__':
    # Ensure the output directory exists
    os.makedirs('crawling_v2/data', exist_ok=True)
    
    # Run the spiders
    run_spiders()