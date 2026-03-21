import yfinance as yf
import json
import os
from datetime import datetime

# ── Lista completa de CEDEARs agrupados por pais y sector ─────────────────

CEDEARES = {
    "US": {
        "name": "Estados Unidos",
        "etf": "SPY",
        "sectors": {
            "Tecnologia": ["AAPL","MSFT","NVDA","GOOGL","META","AMZN","AMD","INTC","CRM","ORCL","ADBE","QCOM","TXN","AVGO","MU"],
            "Finanzas": ["JPM","BAC","WFC","GS","MS","BLK","AXP","V","MA","C"],
            "Salud": ["JNJ","PFE","MRK","ABBV","LLY","UNH","CVS","MDT","BMY","AMGN"],
            "Consumo discrecional": ["TSLA","NKE","MCD","SBUX","HD","TGT","LOW","BKNG","CMG"],
            "Energia": ["XOM","CVX","COP","SLB","EOG","PXD","MPC","VLO"],
            "Comunicaciones": ["NFLX","DIS","CMCSA","T","VZ","TMUS","SPOT","WBD"],
            "Industria": ["BA","CAT","GE","HON","UPS","RTX","LMT","DE","MMM"],
            "Consumo basico": ["PG","KO","PEP","WMT","COST","CL","MO","PM"],
            "Materiales": ["LIN","APD","ECL","NEM","FCX","NUE","AA"],
            "Utilities": ["NEE","DUK","SO","AEP","EXC","D","PCG"]
        }
    },
    "BR": {
        "name": "Brasil",
        "etf": "EWZ",
        "sectors": {
            "Energia": ["PBR","PBR-A"],
            "Finanzas": ["ITUB","BBD","BSBR"],
            "Materiales": ["VALE","GGB","SID"],
            "Consumo basico": ["ABEV"],
            "Utilities": ["CIG","ELP","ERJ"]
        }
    },
    "CN": {
        "name": "China",
        "etf": "MCHI",
        "sectors": {
            "Tecnologia": ["BABA","JD","BIDU","NTES","VIPS"],
            "Consumo discrecional": ["NIO","LI","XPEV","PDD"],
            "Finanzas": ["FUTU"],
            "Comunicaciones": ["TCOM"]
        }
    },
    "DE": {
        "name": "Alemania",
        "etf": "EWG",
        "sectors": {
            "Consumo discrecional": ["BMWYY","VWAGY","DDAIF"],
            "Industria": ["SIEGY","DPSGY"],
            "Salud": ["BAYRY","RHHBY"],
            "Finanzas": ["DB"],
            "Quimicos": ["BASFY"]
        }
    },
    "GB": {
        "name": "Reino Unido",
        "etf": "EWU",
        "sectors": {
            "Energia": ["BP","SHEL"],
            "Finanzas": ["HSBC","BCS","LYG","AZ"],
            "Consumo basico": ["DEO","BTI"],
            "Salud": ["AZN","GSK"]
        }
    },
    "CA": {
        "name": "Canada",
        "etf": "EWC",
        "sectors": {
            "Energia": ["ENB","SU","CVE"],
            "Finanzas": ["TD","RY","BMO","BNS","CM"],
            "Materiales": ["ABX","NTR"],
            "Industria": ["CNI","CP","WSP"]
        }
    },
    "JP": {
        "name": "Japon",
        "etf": "EWJ",
        "sectors": {
            "Tecnologia": ["SONY","NTDOY","KYOCY"],
            "Consumo discrecional": ["TM","HMC","NSANY"],
            "Finanzas": ["MFG","SMFG","MTU"]
        }
    }
}

RATIOS = ["trailingPE","forwardPE","enterpriseToEbitda","pegRatio","priceToBook"]

def fetch_ticker(symbol):
    try:
        info = yf.Ticker(symbol).info
        result = {"ticker": symbol, "name": info.get("shortName", symbol)}
        for r in RATIOS:
            val = info.get(r)
            result[r] = round(val, 2) if isinstance(val, (int, float)) else None
        return result
    except Exception as e:
        print("  ERROR con " + symbol + ": " + str(e))
        return {"ticker": symbol, "name": symbol, **{r: None for r in RATIOS}}

def sector_averages(companies):
    avgs = {}
    for r in RATIOS:
        vals = [c[r] for c in companies if c[r] is not None]
        avgs[r] = round(sum(vals) / len(vals), 2) if vals else None
    return avgs

def main():
    print("Iniciando descarga de datos...")
    output = {"updated": datetime.now().strftime("%Y-%m-%d %H:%M"), "countries": {}}

    for country_code, country_data in CEDEARES.items():
        print("")
        print("Procesando: " + country_data["name"])

        print("  -> ETF " + country_data["etf"])
        etf_data = fetch_ticker(country_data["etf"])

        country_output = {
            "name":    country_data["name"],
            "etf":     etf_data,
            "sectors": {}
        }

        for sector_name, tickers in country_data["sectors"].items():
            print("  -> Sector: " + sector_name)
            companies = []
            for t in tickers:
                print("     " + t)
                companies.append(fetch_ticker(t))

            country_output["sectors"][sector_name] = {
                "companies": companies,
                "averages":  sector_averages(companies)
            }

        output["countries"][country_code] = country_output

    # Guardar JSON
    out_path = os.path.join(os.path.dirname(__file__), "..", "web", "public", "data.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("")
    print("LISTO - Datos guardados en web/public/data.json")
    print("Actualizado: " + output["updated"])

if __name__ == "__main__":
    main()