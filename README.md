## Saudi Stock Exchange (Tadawul) Data App

A data application for pulling historical stock data from the Financial Modeling Prep (FMP) API into MongoDB, then visualizing it with Streamlit.

### Installation

1. Clone the repository:

```bash
git clone https://github.com/cyancaesar/saudi-stock-exchange.git
cd saudi-stock-exchange
```

2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Set up .env file:

- Rename .env.example to .env
- Add your keys

```ini
API_KEY=YOUR_FMP_API_KEY
BASE_URL=https://financialmodelingprep.com/api/v3
MONGODB_URI=mongodb://localhost:27017
```

### Usage

#### 1. Seed the Database

```bash
python main.py seed
```

#### 2. Running Streamlit

```bash
python main.py app
```
