import datetime
from . import snp500, xlb, xlc, xle, xlf, xli, xlk, xlp, xlre, xlu, xlv, xly

ALL_SCRAPERS = [snp500, xlb, xlc, xle, xlf, xli, xlk, xlp, xlre, xlu, xlv, xly]

def run_scrapers():
    for scraper in ALL_SCRAPERS:
        scraper.scrape()


if __name__ == '__main__':
    run_scrapers()
