from index_monkey.scrapers import scrape_ssga

INDEX_NAME = 'XLE'
URL = 'https://www.ssga.com/us/en/intermediary/etfs/library-content/products/fund-data/etfs/us/holdings-daily-us-en-xle.xlsx'


def scrape():
    return scrape_ssga(URL, INDEX_NAME)
