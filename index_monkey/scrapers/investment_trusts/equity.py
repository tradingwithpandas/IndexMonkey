import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import html
import yahooquery as yq
import numbers
from index_monkey.model import new_engine, CON
from index_monkey.scrapers.investment_trusts import INV_TRUST_MAP, UNMATCHED_NAME_UK_TICKER_MAP
import logging

logger = logging.getLogger(__name__)


class InvTrustHoldings:

    @staticmethod
    def get_uk_or_us_listed_ticker(name):
        uk_ticker = None
        us_ticker = None
        clean_name = name.replace('&', 'and')
        search_results = yq.search(clean_name)
        if search_results['quotes']:
            for quote in search_results['quotes']:
                if quote['exchange'] == 'LSE' and uk_ticker is None:
                    uk_ticker = quote['symbol']
                    break
                elif quote['exchange'] in ('NYQ', 'NMS') and us_ticker is None:
                    us_ticker = quote['symbol']
        uk_ticker = UNMATCHED_NAME_UK_TICKER_MAP.get(name, name) if uk_ticker is None else uk_ticker
        ticker = uk_ticker or us_ticker or name
        return ticker


    @staticmethod
    def get_inv_trust_top_10(inv_trust_name):
        url = INV_TRUST_MAP[inv_trust_name]["holdings"]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        tables = soup.find_all("table")
        if len(tables) >= 2:
            holdings_table = soup.find_all("table")[1]
            holdings_df = pd.read_html(str(holdings_table))[0]
            holdings_df['ticker'] = holdings_df['Investment'].apply(lambda inv: InvTrustHoldings.get_uk_or_us_listed_ticker(inv))

            tree = html.fromstring(response.content)
            holdings_date = tree.xpath('/html/body/div[1]/div/main/div/div/div/div[2]/div/div/div[2]/div[1]/p/strong')[0].text
            holdings_date = datetime.datetime.strptime(holdings_date, '%d/%m/%Y').date()
            holdings_df['trust'] = INV_TRUST_MAP[inv_trust_name]['ticker']
            holdings_df['hdate'] = holdings_date
            holdings_df['% of total assets'] = holdings_df['% of total assets'] / 100
            holdings_df['qty'] = 0
            holdings_df = holdings_df.rename(columns={'Investment': 'name', '% of total assets': 'weight'})
            return holdings_df

    @staticmethod
    def insert_holding_row(hdate, trust, name, ticker, weight, qty):
        query = f'''
        INSERT INTO inv_trust_holdings
        VALUES ('{hdate}',
        '{trust}',
        '{name}',
        '{ticker}',
        {weight},
        {qty})
        ON CONFLICT (hdate, trust, name, ticker) DO UPDATE SET
        weight='{weight}',
        qty='{qty}'
        '''
        CON.execute(query)
        CON.commit()

    @staticmethod
    def upload_holdings():
        for trust in INV_TRUST_MAP:
            logger.info(f'fetching {trust}')
            trust_holdings = InvTrustHoldings.get_inv_trust_top_10(trust)
            if trust_holdings is not None:
                for row in trust_holdings.iterrows():
                    InvTrustHoldings.insert_holding_row(
                        row[1]['hdate'],
                        row[1]['trust'],
                        row[1]['name'],
                        row[1]['ticker'],
                        row[1]['weight'],
                        row[1]['qty'],
                    )
                logger.info(f'finished fetching {trust}')
            else:
                logger.info(f'nothing to fetch for {trust}')


def _clean_inv_trust_stats_record(stats_df_raw):
    stats_records = stats_df_raw.to_dict(orient='records')

    cleaned_records = []
    for record in stats_records:
        cleaned_record = {}
        for key, val in record.items():
            cleaned_key = key.replace('(m)', '')
            cleaned_key = cleaned_key.replace('(%)', '')
            cleaned_key = cleaned_key.replace('(last close)', '')
            cleaned_key = cleaned_key.strip()
            if isinstance(val, numbers.Number):
                if '(m)' in key:
                    cleaned_record[cleaned_key] = val * 1e6
                if '(%)' in key:
                    cleaned_record[cleaned_key] = val / 100
                else:
                    cleaned_record[cleaned_key] = val
            elif 'ongoing charge' in key.lower():
                ongoing_charge, ongoing_charge_last_review = val.split()
                ongoing_charge = float(ongoing_charge)
                ongoing_charge_last_review = datetime.datetime.strptime(ongoing_charge_last_review,
                                                                        '(%d/%m/%Y)').date()
                cleaned_record['charge'] = ongoing_charge
                cleaned_record['charge_last_review'] = ongoing_charge_last_review
            else:
                cleaned_record[cleaned_key] = val
        cleaned_records.append(cleaned_record)
    stats_df = pd.DataFrame(cleaned_records)
    stats_df = stats_df.rename(columns={
        'Total assets': 'total_assets',
        'Market Cap': 'mkt_cap',
        'NAV': 'nav',
        'Price': 'close',
        'Gearing': 'gearing',
        'Dividend yield': 'div_yield',
    })
    return stats_df


def get_inv_trust_stats(inv_trust_name):
    url = INV_TRUST_MAP[inv_trust_name]["stats"]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }
    logger.info(f'sending request for {inv_trust_name}')
    response = requests.get(url, headers=headers)
    logger.info(f'got response for {inv_trust_name}')
    soup = BeautifulSoup(response.content, "html.parser")

    stats_table = soup.find_all("table")[0]
    stats_df_raw = pd.read_html(str(stats_table))[0]

    stats_df = _clean_inv_trust_stats_record(stats_df_raw)

    tree = html.fromstring(response.content)

    stats_date = tree.xpath('/html/body/div[1]/div/main/div/div/div/div[2]/div/div/div[2]/div[1]/p/strong')[0].text
    stats_date = datetime.datetime.strptime(stats_date, '%d/%m/%Y').date()

    sector = tree.xpath("/html/body/div[1]/div/main/div/div/div/div[2]/div/div/div[5]/div[2]/a")[0].text

    shares_out = float(tree.xpath("/html/body/div[1]/div/main/div/div/div/div[2]/div/div/div[17]/div[1]/div[1]/div[1]/div[2]")[0].text.replace(',', ''))
    tsy_shares = float(tree.xpath("/html/body/div[1]/div/main/div/div/div/div[2]/div/div/div[17]/div[1]/div[1]/div[2]/div[2]")[0].text.replace(',', ''))

    stats_df['shares_out'] = shares_out
    stats_df['tsy_shares'] = tsy_shares
    stats_df['sector'] = sector.strip()
    stats_df['ticker'] = INV_TRUST_MAP[inv_trust_name]['ticker']
    stats_df['sdate'] = stats_date
    # stats_df = stats_df[['sdate', 'ticker', 'sector', 'total_assets', 'mkt_cap', 'nav', 'close', 'gearing', 'charge',
    #                      'charge_last_review', 'div_yield', 'shs_outstanding', 'tsy_shs', ]]
    return stats_df


def upload_stats():
    for trust in INV_TRUST_MAP:
        logger.info(f'fetching {trust}')
        trust_stats = get_inv_trust_stats(trust)
        trust_stats.to_sql('inv_trust_stats', new_engine, if_exists='append', index=False)
        logger.info(f'finished fetching {trust}')


if __name__ == '__main__':
    InvTrustHoldings.upload_holdings()
