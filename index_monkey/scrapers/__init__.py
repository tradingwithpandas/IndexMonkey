import datetime
from io import BytesIO

import pandas as pd
import urllib

from ..model import engine
from ..ref_data import SCRAPER_TICKER_MAP
from openpyxl import load_workbook


def ssga_base_processing_fn(row_list, eff_date, index_name):
    name = row_list[0]
    ticker = SCRAPER_TICKER_MAP.get(row_list[1]) or row_list[1]
    weight = row_list[4]
    sector = row_list[5]
    shares = row_list[6]
    if sector.lower() != 'unassigned':
        cleaned_row = {
            'idate': eff_date,
            'indexname': index_name,
            'ticker': ticker,
            'sector': sector,
            'name': name,
            'shares': shares,
            'weight': weight,
        }
        return cleaned_row


def parse_ssga_date(date_row):
    date_str_cell = date_row[1].value
    eff_datetime = datetime.datetime.strptime(date_str_cell, 'As of %d-%b-%Y')
    eff_date = eff_datetime.date()
    return eff_date


def scrape_ssga(url, index_name, processing_fn=None):
    resp_file = urllib.request.urlopen(url)
    if resp_file.status == 200:
        index_members_xl = load_workbook(BytesIO(resp_file.read()))
        index_members_sheet = index_members_xl.get_sheet_by_name('holdings')
        index_members_sheet_rows = list(index_members_sheet.rows)
        date_row = index_members_sheet_rows[2]
        eff_date = parse_ssga_date(date_row)
        cleaned_rows = []
        for row in index_members_sheet_rows[5:-19]:
            row_list = [(cell.value or '') for cell in row]

            if processing_fn:
                cleaned_row = processing_fn(row_list, eff_date, index_name)
            else:
                cleaned_row = ssga_base_processing_fn(row_list, eff_date, index_name)

            if cleaned_row:
                cleaned_rows.append(cleaned_row)

        cleaned_index_members_df = pd.DataFrame(cleaned_rows)
        cleaned_index_members_df.to_sql('index_membership', con=engine, if_exists='append', index=False)
        return cleaned_index_members_df
