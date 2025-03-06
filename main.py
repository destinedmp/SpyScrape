import streamlit as st
import stockfuncs as sf
from fmp_python.fmp import FMP
from google import genai

def initializeSessionState():
    """Initialize Streamlit session state variables"""
    if "ticker" not in st.session_state:
        st.session_state.ticker = "NVDA"
    if "growthRate" not in st.session_state:
        st.session_state.growthRate = 0.05  # Default growth rate
    if "intrinsicPrice" not in st.session_state:
        st.session_state.intrinsicPrice = None  # Store calculated intrinsic price

def main():
    # Initialize session state variables
    initializeSessionState()

    # Load API keys from Streamlit secrets
    fmp = FMP(api_key=st.secrets["api_key"])
    client = genai.Client(api_key=st.secrets["api_key2"])  # Gemini API Key
    
    # Page Title
    st.title("📈 Discounted Cash Flow Analysis")
    st.markdown("Analyze stocks and estimate their intrinsic value based on financial data.")

    # Ticker Input Section
    col1, col2 = st.columns([4, 1])

    with col1:
        tickerInput = st.text_input(
            "Enter a company name/ticker:",
            value=st.session_state.ticker,
            key="ticker_input"
        )

    with col2:
        # Aligning the search button with text input
        if st.button("🔍 Auto-Suggest Ticker Symbol", key="search_button"):
            tickerSymbol = sf.findTickerSymbol(tickerInput, client)
            if tickerSymbol:
                st.session_state.ticker = tickerSymbol
                st.rerun()

    # Update session state when ticker input changes
    if tickerInput != st.session_state.ticker:
        st.session_state.ticker = tickerInput
        st.rerun()

    # Process if ticker exists
    if st.session_state.ticker:
        st.divider()

        try:
            # Retrieve and display financial data
            financialData = sf.displayFinancialData(st.session_state.ticker)
            
            if financialData:
                fcfList, cash, debt, reqRate = financialData

                # Display Financial Data
                st.subheader("📊 Financial Data (in millions)")
                st.markdown("All values below are in **millions of dollars**")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(label="📉 Free Cash Flow (FCF)", value=f"${fcfList[0]:,.2f}")
                    st.metric(label="💰 Cash on Hand", value=f"${cash:,.2f}")

                with col2:
                    st.metric(label="💸 Total Debt", value=f"${debt:,.2f}")
                    st.metric(label="📊 Required Rate of Return (WACC)", value=f"{reqRate:.2%}")  # Display WACC as percentage

                st.divider()

                # Growth Rate Input Section
                st.subheader("📈 Growth Rate Input")
                col1, col2 = st.columns([4, 1])

                with col1:
                    growthRateInput = st.text_input(
                        "Expected Cash Flow Growth Rate (decimal):",
                        value=str(st.session_state.growthRate),
                        key="growth_rate_input"
                    )

                    # Update session state when growth rate input changes
                    if growthRateInput != str(st.session_state.growthRate):
                        st.session_state.growthRate = float(growthRateInput)
                        st.rerun()

                with col2:
                    # Aligning the auto-suggest growth rate button with the text input
                    if st.button("⚡ Auto-Suggest Growth Rate", key="growth_rate_button"):
                        suggestedRate = sf.suggestGrowthRate(st.session_state.ticker, client)
                        if suggestedRate is not None:
                            st.session_state.growthRate = suggestedRate
                            st.rerun()

                st.divider()

                # Ensure valid financial data before calculating intrinsic price
                if fcfList and cash is not None and debt is not None and reqRate is not None:
                    shares_outstanding = fmp.get_quote(st.session_state.ticker)[0]["sharesOutstanding"] / 1_000_000
                    st.session_state.intrinsicPrice = sf.calculateIntrinsicPrice(
                        fcfList[0], 
                        st.session_state.growthRate, 
                        reqRate, 
                        cash, 
                        debt, 
                        shares_outstanding
                    )

                    # Display Intrinsic Value
                    st.subheader("💎 Intrinsic Stock Value")
                    st.markdown(f"Based on the provided data, the **intrinsic stock price** is:")
                    st.success(f"💲 **${st.session_state.intrinsicPrice:.2f} per share**")

                else:
                    st.error("❌ Error: Some financial data is missing.")
            else:
                st.error("❌ Error: Could not retrieve financial data. Please ensure the ticker is correct or try another company.")

        except Exception as e:
            st.error(f"❌ Error: Could not retrieve financial data for **{st.session_state.ticker}**. Please ensure the ticker is correct or try another company.")

if __name__ == "__main__":
    main()
