import datetime
from typing import Dict
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import json

from waste_collection_schedule import Collection  # type: ignore[attr-defined]

TITLE = "Wychavon UK"
DESCRIPTION = "Wychavon, Worcestershire, UK bin collection schedule."
URL = "https://selfservice.wychavon.gov.uk"
TEST_CASES = {
    "Post Office": {"postcode": "WR11 4HR", "address": "Wickhamford Post Office, 43 Pitchers Hill, Wickhamford, EVESHAM", "alAddrsel": 100120696017}
}

class Source:

    def __init__(self, postcode="WR11 4HR", address="Wickhamford Post Office, 43 Pitchers Hill, Wickhamford, EVESHAM", alAddrsel=100120696017):
        self._postcode = postcode
        self._address = address
        self._alAddrsel = alAddrsel
        self.url = 'https://selfservice.wychavon.gov.uk/wdcroundlookup/HandleSearchScreen'

    def fetch(self):

        request_headers = {
            "Connection":"keep-alive",
            "Cache-Control":"max-age=0",
            "Origin":"https://selfservice.wychavon.gov.uk",
            "Upgrade-Insecure-Requests":"1",
            "DNT":"1",
            "Content-Type":"application/x-www-form-urlencoded",
            "User-Agent":"Mozilla/5.0 (X11; CrOS armv7l 12105.68.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.88 Safari/537.36",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Referer":"https://selfservice.wychavon.gov.uk/wdcroundlookup/wdc_search.jsp",
            "Accept-Encoding":"gzip, deflate, br",
            "Accept-Language":"en-GB,en-US;q=0.9,en;q=0.8",
            "Cookie":"JSESSIONID=504f1d24b6b7129559dfbd6bc348; _ga=GA1.3.1756409093.1564257616; _gid=GA1.3.1287027304.1564257616; _gat_gtag_UA_141488549_2=1"
        }
        req_data = {
            "nmalAddrtxt":quote_plus(self._postcode),
            "alAddrsel":str(self._alAddrsel),
            "txtPage":"std",
            "txtSearchPerformedFlag":"false",
            "futuredate":"",
            "errstatus":"",
            "address":self._address,
            "jsenabled":"TsOkrIPJrqo5nVGVChHj",
            "btnSubmit":"Next"
        }    

        response = requests.post(self.url, headers=request_headers, data=req_data)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.select('table tr')
        

        bins = {
            "black": [
                rows[0].find('strong').text.strip(),
                rows[0].find('br').next_sibling.strip()
            ],
            "green": [
                rows[1].find('strong').text.strip(),
                rows[1].find('br').next_sibling.strip()
            ]
        }

        entries = []
        for bin_type in bins:
            bin_icon = "mdi:trash-can" if bin_type is "black" else "mdi:recycle"
            for bin_str in bins[bin_type]:
                bin_day = bin_str.split()[0]
                bin_date = datetime.datetime.strptime(bin_str.split()[1],'%d/%m/%Y').date()
                entries.append(
                    Collection(
                        date = bin_date,
                        t = bin_type,
                        icon = bin_icon
                    )
                )

        return entries
