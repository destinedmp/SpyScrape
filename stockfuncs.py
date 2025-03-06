from bs4 import BeautifulSoup
import requests

def findTickerSymbol(companyName, client):
    """
    Use Gemini AI to find the stock ticker symbol for a given company name.

    Args:
        companyName (str): The name of the company.
        client (genai.Client): The Gemini AI client.

    Returns:
        str: The stock ticker symbol in uppercase.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[f"Answer in one word only. What is the stock ticker for {companyName}?"]
        )
        return response.text.strip().upper()
    except Exception as e:
        raise Exception(f"Error finding ticker: {e}")

def suggestGrowthRate(ticker, client):
    """
    Use Gemini AI to estimate the expected growth rate of a stock's cash flow.

    Args:
        ticker (str): The stock ticker.
        client (genai.Client): The Gemini AI client.

    Returns:
        float: The estimated growth rate in decimal form.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[f"Answer in one word only and as a decimal. Estimate {ticker} cash flow growth rate?"]
        )
        return float(response.text.strip())
    except Exception as e:
        raise Exception(f"Error generating growth rate: {e}")

def calculateIntrinsicPrice(fcf, growthRate, reqRate, cash, debt, sharesOutstanding):
    """
    Calculate the intrinsic stock price using the Discounted Cash Flow (DCF) method.

    Args:
        fcf (float): Free Cash Flow of the company.
        growthRate (float): Expected growth rate of cash flows.
        reqRate (float): Required rate of return (WACC).
        cash (float): Cash on hand.
        debt (float): Total company debt.
        sharesOutstanding (float): Number of shares outstanding.

    Returns:
        float: The intrinsic stock price.
    """
    perpetualRate = 0.019  # Assumed perpetual growth rate

    # Forecast Future Cash Flows (for 5 years)
    cashProjections = [fcf * (1 + growthRate) ** year for year in range(1, 6)]

    # Terminal Value Calculation
    terminalValue = (cashProjections[-1] * (1 + perpetualRate)) / (reqRate - perpetualRate)

    # Discount Cash Flows to Present Value
    presentValues = [cf / (1 + reqRate) ** (i + 1) for i, cf in enumerate(cashProjections)]
    presentValues.append(terminalValue / (1 + reqRate) ** 5)

    # Compute Equity Value
    equityValue = sum(presentValues) + cash - debt

    # Compute Intrinsic Stock Price
    return equityValue / sharesOutstanding

def scraper(url, rowName):
    """
    Scrape data from StockAnalysis.

    Args:
        url (str): The webpage URL.
        rowName (str): The row name to extract data from.

    Returns:
        list: Extracted float values from the row.
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table')

    if not table:
        raise ValueError("No table found on the page.")

    rows = table.find_all('tr')
    for row in rows:
        cols = [ele.text.strip() for ele in row.find_all(['td', 'th'])]  # Extract row text
        if cols and cols[0] == rowName:
            return [float(item.replace(',', '')) for item in cols[1:] if item != 'Upgrade']  # Convert to float

def findFCF(stock):
    """Retrieve Free Cash Flow (FCF) values."""
    url = f"https://stockanalysis.com/stocks/{stock}/financials/"
    return scraper(url, 'Free Cash Flow')

def findCash(stock):
    """Retrieve Cash & Short-Term Investments value."""
    url = f"https://stockanalysis.com/stocks/{stock}/financials/balance-sheet/"
    return scraper(url, 'Cash & Short-Term Investments')[0]

def findDebt(stock):
    """Retrieve Total Debt value."""
    url = f"https://stockanalysis.com/stocks/{stock}/financials/balance-sheet/"
    return scraper(url, 'Total Debt')[0]

def findWACC(stock):
    """Retrieve Weighted Average Cost of Capital (WACC) value."""
    url = f"https://www.validea.com/factor-report/{stock}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    waccCell = soup.find('a', href="/definitions/weighted-average-cost-of-capital").find_next('span')
    if not waccCell:
        raise ValueError("WACC data not found.")

    return float(waccCell.text.strip('%')) / 100

def displayFinancialData(ticker):
    """
    Retrieve financial data for a stock.

    Args:
        ticker (str): The stock ticker.

    Returns:
        tuple: (Free Cash Flow List, Cash, Debt, WACC)
    """
    try:
        fcfList = findFCF(ticker)
        cash = findCash(ticker)
        debt = findDebt(ticker)
        reqRate = findWACC(ticker)
        
        return fcfList, cash, debt, reqRate
    except Exception as e:
        raise Exception(f"Error retrieving financial data: {e}")
