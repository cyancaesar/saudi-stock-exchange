from src.config import setup_environment_and_logging
import pandas as pd
from src.db import DB
from src.fmp import FMP
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = setup_environment_and_logging()

def process_symbol(symbol_data: dict, db: DB):
    symbol = symbol_data['symbol']
    logger.info(f"[{symbol}] Extracting historical data")

    historical = FMP().historical(symbol=symbol)
    
    if not historical or "historical" not in historical or not len(historical["historical"]):
        logger.warning(f"[{symbol}] No historical data found")
        with open("symbol_not_found.txt", "a+") as f:
            f.write(symbol + "\n")
        return

    df = pd.DataFrame.from_dict(historical['historical'])
    df.insert(loc=0, column="symbol", value=symbol)
    df["date"] = pd.to_datetime(df["date"])

    db.load_into_mongo(df)
    
    logger.info(f"[{symbol}] Loaded {len(df)} rows")

def seed(max_workers=3):
  logger.info("Starting database seeding process")
  
  db = DB()
  db.init_mongo()
  symbols = FMP().exchange_symbols("SAU") # Fetch all symbols listed in Saudi Stock Market (Tadawul)
  logger.info(f"Retrieved Tadawul symbols list total of {len(symbols)}")

  # Process symbols historical data concurrently
  futures = []
  with ThreadPoolExecutor(max_workers=max_workers) as executor:
      for symbol_data in symbols:
          futures.append(
              executor.submit(process_symbol, symbol_data, db)
          )

      for future in as_completed(futures):
          exc = future.exception()
          if exc:
              logger.error(f"Exception in thread: {exc}")

  logger.info("Seeding has finished successfully")