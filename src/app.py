from src.config import setup_environment_and_logging
import pandas as pd
import streamlit as st
from src.db import DB
from src.fmp import FMP
from millify import millify

logger = setup_environment_and_logging()

@st.cache_data
def cachable_load_from_mongo():
  db = DB()
  db.init_mongo()
  df = db.load_from_mongo()

  if df.empty:
    st.error("No data found in the database.")
    st.stop()

  df['date'] = pd.to_datetime(df['date'])
  df.set_index('date', inplace=True)
  df = df.sort_index()
  return df

def chart_tab(df):
  st.area_chart(df['close'])
  st.subheader("Stock Data")
  st.dataframe(df, use_container_width=True)

def company_info_block():
  fmp = FMP()
  profile = fmp.company_profile(selected_symbol)[0]

  st.subheader("Company Profile")

  col1, col2 = st.columns([1, 4])

  with col1:
    st.image(profile['image'])
  with col2:
    st.write(f"**Symbol**: {profile['symbol']}")
    st.write(f"**Company Name**: {profile['companyName']}")
    st.write(f"**Industry**: {profile['industry']}")
    st.write(f"**Sector**: {profile['sector']}")
    st.write(f"**Website**: {profile['website']}")
    st.write(f"**CEO**: {profile['ceo']}")
    st.write(f"**Description**: {profile['description'][0:250]}...")

def stock_info_block():
  fmp = FMP()
  stock = fmp.quote_full(selected_symbol)[0]
  company = fmp.company_profile(selected_symbol)[0]
  exchange = fmp.exchange_trading_hours("SAU")
  isMarketOpen = exchange['isMarketOpen']

  priceOpen = stock['open']
  high = stock['dayHigh']
  low = stock['dayLow']
  price = stock['price']
  change = stock['change']
  changesPercentage = stock['changesPercentage']
  prevClose = stock['previousClose']
  eps = stock['eps']
  pe = stock['pe']
  earningsAnnouncement = stock['earningsAnnouncement']
  sharesOutstanding = stock['sharesOutstanding']
  marketCap = stock['marketCap']
  volume = stock['volume']
  avgVolume = stock['avgVolume']
  priceAvg50 = stock['priceAvg50']
  priceAvg200 = stock['priceAvg200']
  timestamp = pd.to_datetime(stock['timestamp'], unit='s').tz_localize('UTC').tz_convert('Asia/Riyadh').strftime('%I:%M:%S %p')
  beta = company['beta']

  st.subheader("Stock Overview")

  col1, col2, col3, col4, col5, col6 = st.columns(6)

  with col1:
    price_helper = f"At close at {timestamp} UTC+03:00" if not isMarketOpen else timestamp
    st.metric(label="Price", value=price, delta=change, help=price_helper)
  with col2:
    st.metric(label="Change", value=round(change, 2))
  with col3:
    st.metric(label="Change %", value=round(changesPercentage, 2))

  col1, col2, col3, col4 = st.columns(4)

  with col1:
    st.metric(label="Open", value=priceOpen, border=True)
    st.metric(label="Volume", value=millify(volume), border=True)
    st.metric(label="Avg. 50 Days Price", value=round(priceAvg50, 2), border=True)
  with col2:
    st.metric(label="High", value=high, border=True)
    st.metric(label="Avg. Volume", value=millify(avgVolume), border=True)
    st.metric(label="Avg. 200 Days Price", value=round(priceAvg200, 2), border=True)
  with col3:
    st.metric(label="Low", value=low, border=True)
    st.metric(label="Market Cap", value=millify(marketCap), border=True)
    st.metric(label="EPS", value=eps, border=True)
  with col4:
    st.metric(label="Previous Close", value=prevClose, border=True)
    st.metric(label="Beta (β)", value=beta, border=True, help="β > 1 means the stock is more volatile than the market, β < 1 means less volatile")
    st.metric(label="P/E", value=pe, border=True)

def profile_tab():
  company_info_block()
  st.divider()
  stock_info_block()


def create_st_app():
    global selected_symbol    
    st.set_page_config(page_title="Tadawul Data App", page_icon="📈", layout="wide")
    
    df = cachable_load_from_mongo()

    st.sidebar.title("Saudi Stock Exchange (Tadawul)")
    
    exchange = FMP().exchange_trading_hours("SAU")

    if exchange['isMarketOpen']:
      st.sidebar.markdown(f"**Market Status**: <span style='color:green;'>Open</span>", unsafe_allow_html=True)
    else:
      st.sidebar.markdown(f"**Market Status**: <span style='color:red;'>Closed</span>", unsafe_allow_html=True)

    st.sidebar.markdown(f"**Market Hours**: {exchange['openingHour']} - {exchange['closingHour']}")

    # Symbol selection
    symbols = df['symbol'].unique()
    selected_symbol = st.sidebar.selectbox("Select Symbol", symbols)

    df_filtered = df[df['symbol'] == selected_symbol]
    
    start_date = st.sidebar.date_input(
    "Start Date", 
    value=df_filtered.index.min().date(), 
    min_value=df_filtered.index.min().date(), 
    max_value=df_filtered.index.max().date()
    )
    end_date = st.sidebar.date_input(
        "End Date", 
        value=df_filtered.index.max().date(), 
        min_value=df_filtered.index.min().date(), 
        max_value=df_filtered.index.max().date()
    )
    

    df_filtered = df_filtered[(df_filtered.index >= pd.to_datetime(start_date)) & (df_filtered.index <= pd.to_datetime(end_date))]

    st.sidebar.download_button(
    label="Download CSV",
    data=df_filtered.to_csv().encode('utf-8'),
    file_name='filtered_stock_data.csv',
    mime='text/csv',
    )

    st.subheader(f"{selected_symbol} Stock Chart")

    tab1, tab2, tab3 = st.tabs(["Chart", "Profile", "Other"])

    with tab1:
      chart_tab(df_filtered)
    
    with tab2:
      profile_tab()

def main():
  try:
    logger.info("Executing")
    create_st_app()

  except KeyboardInterrupt:
    logger.info("Cleaning up")

if __name__ == "__main__":
  main()