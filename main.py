
import yfinance as yf
import numpy as np
import stockfuncs as sf
ticker = input("Enter Ticker: ").strip()  # User enters ticker
stake = yf.Ticker(ticker)
try:
     # Retrieve financial data
     fcfList = sf.findFCF(ticker)  
     cash = sf.findCash(ticker)
     debt = sf.findDebt(ticker)
     reqRate = sf.findWACC(ticker)  # Required Rate

     # Forecast parameters
     perpRate = 0.019  # Perpetual Rate (manual entry)
     growthRate = float(input("Enter expected cash flow growth rate (as decimal): ").strip())  # 

     # Forecast future cash flows
     fcf = fcfList[0]
     cashProj = [fcf * (1 + growthRate) ** year for year in range(1, 6)]

     # Calculate terminal value
     tv = (cashProj[-1] * (1 + perpRate)) / (reqRate - perpRate)

     # Calculate present value of cash flows and terminal value
     present_values = [cf / (1 + reqRate) ** (i + 1) for i, cf in enumerate(cashProj)]
     present_values.append(tv / (1 + reqRate) ** 5)

     # Sum of present values
     equity_value = np.sum(present_values) + cash - debt

     # Calculate intrinsic stock price
     shares_outstanding = stake.info["sharesOutstanding"] / 1_000_000  # Convert to millions
     intrinsic_price = equity_value / shares_outstanding
     print(f"Intrinsic Stock Price: ${intrinsic_price:.2f}")

except Exception as e:
     print(f"An error occurred: {e}")