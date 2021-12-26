from index_monkey.scrapers import scrape_ssga

INDEX_NAME = '^GSPC'  # This is the S&P500 index ticker on Yahoo Finance
URL = 'https://www.ssga.com/us/en/intermediary/etfs/library-content/products/fund-data/etfs/us/holdings-daily-us-en-splg.xlsx'


def scrape():
    return scrape_ssga(URL, INDEX_NAME)
