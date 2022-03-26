from index_monkey.scrapers import scrape_ssga

INDEX_NAME = 'XLK'
URL = 'https://www.ssga.com/us/en/individual/etfs/library-content/products/fund-data/etfs/us/holdings-daily-us-en-xlk.xlsx'


def scrape():
    return scrape_ssga(URL, INDEX_NAME)
