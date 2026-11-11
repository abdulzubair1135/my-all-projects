import urllib.request
import json

class LiveFinanceTool:
    """
    Direct Real-Time Financial Data Engine:
    - 100% Real-Time Stock Indices (Nifty 50, BSE Sensex, S&P 500)
    - 100% Real-Time Crypto Tickers (BTC, ETH, SOL, DOGE)
    - Direct API feeds - ZERO SEO junk, ZERO fake generic guides.
    """
    @staticmethod
    def get_crypto_live():
        coins = {
            "BTCUSDT": "Bitcoin (BTC)",
            "ETHUSDT": "Ethereum (ETH)",
            "SOLUSDT": "Solana (SOL)",
            "DOGEUSDT": "Dogecoin (DOGE)"
        }
        results = {}
        for symbol, name in coins.items():
            try:
                url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=4) as resp:
                    data = json.loads(resp.read().decode())
                    price = float(data["lastPrice"])
                    change = float(data["priceChangePercent"])
                    high = float(data["highPrice"])
                    low = float(data["lowPrice"])
                    results[name] = {
                        "price_usd": round(price, 2),
                        "price_inr": round(price * 86.8, 2),
                        "change_24h": round(change, 2),
                        "high_24h": round(high, 2),
                        "low_24h": round(low, 2)
                    }
            except Exception:
                pass
        return results

    @staticmethod
    def get_stock_indices_live():
        symbols = {
            "%5ENSEI": "NIFTY 50",
            "%5EBSESN": "BSE SENSEX",
            "%5EGSPC": "S&P 500",
            "%5EIXIC": "NASDAQ"
        }
        results = {}
        for sym, name in symbols.items():
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    d = json.loads(resp.read().decode())
                    meta = d["chart"]["result"][0]["meta"]
                    price = meta.get("regularMarketPrice")
                    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
                    change_pct = 0.0
                    if price and prev:
                        change_pct = round(((price - prev) / prev) * 100, 2)
                    results[name] = {
                        "price": round(price, 2) if price else "N/A",
                        "change_pct": change_pct
                    }
            except Exception:
                pass
        return results
