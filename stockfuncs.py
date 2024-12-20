from bs4 import BeautifulSoup
import requests

def scraper(url, rowName):
    """
    Get data from StockAnalysis

    Args:
        url (str): URL of the webpage.
        rowName (str): Name of the row to get data from.

    Returns:
        list: Float values of desired row.
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table')

    if not table:
        raise ValueError("No table found on the page.")

    rows = table.find_all('tr')
    for row in rows:
        cols = [ele.text.strip() for ele in row.find_all(['td', 'th'])] # Strip all text in the row
        if cols and cols[0] == rowName:
            return [float(item.replace(',', '')) for item in cols[1:] if item != 'Upgrade'] # Remove all commas between numbers, upgrade column and convert to a float

def findFCF(stock):
    """
    Get Free Cash Flow (FCF).

    Args:
        stock (str): Stock ticker.

    Returns:
        list: FCF values in millions.
    """
    url = f"https://stockanalysis.com/stocks/{stock}/financials/"
    return scraper(url, 'Free Cash Flow')

def findCash(stock):
    """
    Get Cash & Short-Term Investments.

    Args:
        stock (str): Stock ticker.

    Returns:
        float: Cash and short-term investments value in millions.
    """
    url = f"https://stockanalysis.com/stocks/{stock}/financials/balance-sheet/"
    return scraper(url, 'Cash & Short-Term Investments')[0]

def findDebt(stock):
    """
    Get Total Debt.

    Args:
        stock (str): Stock ticker.

    Returns:
        float: Total debt value in millions.
    """
    url = f"https://stockanalysis.com/stocks/{stock}/financials/balance-sheet/"
    return scraper(url, 'Total Debt')[0]
def findWACC(stock):
    """
    Find weighted average cost of capital (WACC) for stock.

    Args:
        stock (str): Stock ticker.

    Returns:
        float: WACC value.
    """
    url = f"https://www.validea.com/factor-report/{stock}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    waccCell = soup.find('a', href="/definitions/weighted-average-cost-of-capital").find_next('span')
    if not waccCell:
        raise ValueError("WACC data not found.")

    wacc = float(waccCell.text.strip('%')) / 100
    return wacc
