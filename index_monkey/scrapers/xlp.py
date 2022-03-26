from index_monkey.scrapers import scrape_ssga

INDEX_NAME = 'XLP'
URL = 'https://www.ssga.com/us/en/intermediary/etfs/library-content/products/fund-data/etfs/us/holdings-daily-us-en-xlp.xlsx'


def scrape():
    return scrape_ssga(URL, INDEX_NAME)
