import yfinance as yf
import json
import os
from datetime import datetime

RATIOS = [
    ("trailingPE",                   "P/E"),
    ("forwardPE",                    "Fwd P/E"),
    ("enterpriseToEbitda",           "EV/EBITDA"),
    ("pegRatio",                     "PEG"),
    ("priceToBook",                  "P/B"),
    ("priceToSalesTrailing12Months", "P/S"),
    ("dividendYield",                "Div Yield"),
    ("returnOnEquity",               "ROE"),
    ("debtToEquity",                 "Debt/Eq"),
    ("profitMargins",                "Margin"),
    ("marketCap",                    "Mkt Cap"),
    ("beta",                         "Beta"),
]

RATIO_KEYS   = [r[0] for r in RATIOS]
RATIO_LABELS = {r[0]: r[1] for r in RATIOS}

COUNTRY_ETFS = {
    "US":"SPY","BR":"EWZ","CN":"MCHI","DE":"EWG","GB":"EWU","CA":"EWC",
    "JP":"EWJ","FR":"EWQ","CH":"EWL","KR":"EWY","IN":"INDA","AU":"EWA",
    "MX":"EWW","ES":"EWP","IT":"EWI","NL":"EWN","SE":"EWD","IL":"EIS",
    "HK":"EWH","TW":"EWT","AR":"ARGT","CL":"ECH","CO":"GXG","ZA":"EZA"
}

COUNTRY_NAMES = {
    "US":"Estados Unidos","BR":"Brasil","CN":"China","DE":"Alemania",
    "GB":"Reino Unido","CA":"Canada","JP":"Japon","FR":"Francia",
    "CH":"Suiza","KR":"Corea del Sur","IN":"India","AU":"Australia",
    "MX":"Mexico","ES":"Espana","IT":"Italia","NL":"Paises Bajos",
    "SE":"Suecia","IL":"Israel","HK":"Hong Kong","TW":"Taiwan",
    "AR":"Argentina","CL":"Chile","CO":"Colombia","ZA":"Sudafrica"
}

SECTOR_MAP = {
    "Technology":               "Tecnologia",
    "Financial Services":       "Finanzas",
    "Healthcare":               "Salud",
    "Consumer Cyclical":        "Consumo discrecional",
    "Consumer Defensive":       "Consumo basico",
    "Energy":                   "Energia",
    "Communication Services":   "Comunicaciones",
    "Industrials":              "Industria",
    "Basic Materials":          "Materiales",
    "Real Estate":              "Inmobiliario",
    "Utilities":                "Utilities",
}

def fetch_ticker(symbol):
    try:
        info = yf.Ticker(symbol).info
        result = {
            "ticker":    symbol,
            "name":      info.get("shortName", symbol),
            "sector":    info.get("sector", ""),
            "industry":  info.get("industry", ""),
        }
        for key in RATIO_KEYS:
            val = info.get(key)
            if key in ("dividendYield","returnOnEquity","profitMargins") and val:
                result[key] = round(val * 100, 2)
            elif key == "marketCap" and val:
                result[key] = round(val / 1e9, 2)
            elif isinstance(val, (int, float)):
                result[key] = round(val, 2)
            else:
                result[key] = None
        return result
    except Exception as e:
        print("  ERROR " + symbol + ": " + str(e))
        return {"ticker": symbol, "name": symbol, "sector": "", "industry": "",
                **{k: None for k in RATIO_KEYS}}

def sector_averages(companies):
    avgs = {}
    for key in RATIO_KEYS:
        vals = [c[key] for c in companies if c[key] is not None]
        if not vals:
            avgs[key] = None
        elif key == "marketCap":
            avgs[key] = round(sum(vals), 2)
        else:
            avgs[key] = round(sum(vals) / len(vals), 2)
    return avgs

def main():
    base = os.path.dirname(__file__)

    valid_path = os.path.join(base, "valid_adrs.json")
    if not os.path.exists(valid_path):
        print("ERROR: no se encuentra valid_adrs.json")
        print("Ejecuta primero: python discover_adrs.py")
        return

    with open(valid_path, "r", encoding="utf-8") as f:
        valid_data = json.load(f)["valid"]

    print("Iniciando descarga de ratios para " +
          str(sum(len(v) for v in valid_data.values())) + " tickers validos...")

    output = {
        "updated":   datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ratios":    RATIO_LABELS,
        "countries": {}
    }

    for country_code, tickers_info in valid_data.items():
        if not tickers_info:
            continue

        country_name = COUNTRY_NAMES.get(country_code, country_code)
        etf_ticker   = COUNTRY_ETFS.get(country_code, "")

        print("")
        print("Procesando: " + country_name + " (" + str(len(tickers_info)) + " tickers)")

        print("  -> ETF " + etf_ticker)
        etf_data = fetch_ticker(etf_ticker) if etf_ticker else {"ticker": "", "name": ""}

        sectors = {}

        for item in tickers_info:
            ticker  = item["ticker"]
            raw_sec = item.get("sector", "") or ""
            raw_ind = item.get("industry", "") or ""

            sector_es = SECTOR_MAP.get(raw_sec, raw_sec if raw_sec else "Otros")
            industry  = raw_ind if raw_ind else "General"

            print("  " + ticker)

            company = fetch_ticker(ticker)
            company["industry"] = industry

            if sector_es not in sectors:
                sectors[sector_es] = {}
            if industry not in sectors[sector_es]:
                sectors[sector_es][industry] = []

            sectors[sector_es][industry].append(company)

        sector_output = {}
        for sec_name, industries in sectors.items():
            all_companies = []
            subsector_out = {}

            for ind_name, companies in industries.items():
                subsector_out[ind_name] = {
                    "companies": companies,
                    "averages":  sector_averages(companies)
                }
                all_companies.extend(companies)

            sector_output[sec_name] = {
                "subsectors": subsector_out,
                "companies":  all_companies,
                "averages":   sector_averages(all_companies)
            }

        output["countries"][country_code] = {
            "name":    country_name,
            "etf":     etf_data,
            "sectors": sector_output
        }

    out_path = os.path.join(base, "..", "web", "public", "data.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("")
    print("LISTO - Datos guardados en web/public/data.json")
    print("Actualizado: " + output["updated"])
    total = sum(
        len(s["companies"])
        for c in output["countries"].values()
        for s in c["sectors"].values()
    )
    print("Total empresas: " + str(total))

if __name__ == "__main__":
    main()
