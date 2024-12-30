from src.config import setup_environment_and_logging
import requests
import os
from urllib.parse import urljoin

logger = setup_environment_and_logging()

class FMP:
  def __init__(self):
    self.api_key = os.getenv("API_KEY")
    self.base_url = os.getenv("BASE_URL")

    if not self.api_key or not self.base_url:
      raise ValueError("API_KEY and BASE_URL must be set in environment variables.")
    
    self.params = {
      "apikey": os.getenv("API_KEY")
    }
    self.session = requests.Session()

  def _do_request(self, path, params=None):
    url = urljoin(self.base_url, path.lstrip("/"))
    params = {**self.params, **(params or {})}
    response = self.session.get(url, params=params)

    try:
      response.raise_for_status()
    except requests.exceptions.HTTPError as e:
      logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
      return None
    
    return response.json()

  def quote_full(self, symbol):
    path = f"/quote/{symbol}"
    return self._do_request(path)
  
  def quote_order(self, symbol):
    path = f"/quote-order/{symbol}"
    return self._do_request(path)
    
  def historical(self, symbol, _from="1990-01-01", _to=None):
    path = f"/historical-price-full/{symbol}"
    params = {"from": _from}
    
    if _to:
      params['to'] = _to
    
    return self._do_request(path, params)
  
  def last_eod(self, symbol):
    path = f"/historical-price-full/{symbol}?serietype=line"
    data = self._do_request(path)
    if data and "historical" in data:
      return data["historical"][-1]
    return None

  def exchange_symbols(self, exchange):
    path = f"/symbol/{exchange}"
    return self._do_request(path)
  
  def exchange_trading_hours(self, exchange):
    path = f"/is-the-market-open-all"
    exchanges = self._do_request(path)
    exchange = [item for item in exchanges if item["exchange"] == exchange]
    return exchange[0] if len(exchange) > 0 else None
  
  def company_profile(self, symbol):
    path = f"/profile/{symbol}"
    return self._do_request(path)