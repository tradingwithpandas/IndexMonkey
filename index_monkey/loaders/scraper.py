from index_monkey.scrapers import snp500, xlb, xlc, xle, xlf, xli, xlk, xlp, xlre, xlu, xlv, xly
import datetime
from index_monkey.loaders.price import PriceLoader

INDEX_NAMES = [
    xlb.INDEX_NAME,
    xlc.INDEX_NAME,
    xle.INDEX_NAME,
    xlf.INDEX_NAME,
    xli.INDEX_NAME,
    xlk.INDEX_NAME,
    xlp.INDEX_NAME,
    xlre.INDEX_NAME,
    xlu.INDEX_NAME,
    xlv.INDEX_NAME,
    xly.INDEX_NAME,
    snp500.INDEX_NAME,
]


def fetch_prices(start_date=None, end_date=None, indices=None):
    start_date = start_date or (datetime.date.today() - datetime.timedelta(days=2))
    end_date = end_date or (datetime.date.today() - datetime.timedelta(days=1))
    indices = indices or INDEX_NAMES
    for index in indices:
        p = PriceLoader(index, start_date, end_date, use_latest_index_weighting=True)
        p.fetch_prices()
        print(f'{index} price scraped between {start_date} and {end_date}')


if __name__ == '__main__':
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=1)
    fetch_prices(start_date=start_date, end_date=end_date)
