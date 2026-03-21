import yfinance as yf
import json
import os

# Lista completa de ADRs por pais basada en NYSE/NASDAQ/AMEX
# Fuente: topforeignstocks.com + finviz geo map
# Solo incluimos empresas con market cap relevante

ADR_BY_COUNTRY = {
    "US": {
        "name": "Estados Unidos",
        "etf": "SPY",
        "tickers": [
            # Tecnologia
            "AAPL","MSFT","NVDA","GOOGL","META","AMZN","AMD","INTC","CRM","ORCL",
            "ADBE","QCOM","TXN","AVGO","MU","NOW","INTU","SNOW","PLTR","UBER",
            "DASH","AMAT","KLAC","LRCX","DELL","HPQ","WDC","NFLX","SNAP","PINS",
            # Finanzas
            "JPM","BAC","WFC","C","GS","MS","BLK","V","MA","AXP",
            "USB","PNC","TFC","COF","DFS","SYF","SCHW","CB","AIG","MET",
            "PRU","AFL","ALL",
            # Salud
            "JNJ","PFE","MRK","ABBV","LLY","UNH","CVS","MDT","BMY","AMGN",
            "GILD","BIIB","VRTX","REGN","MRNA","ABT","SYK","BSX","ISRG","CI",
            "HUM","CNC",
            # Consumo discrecional
            "TSLA","NKE","MCD","SBUX","HD","TGT","LOW","BKNG","CMG","GM",
            "F","RIVN","COST","TJX","ROST","YUM","DPZ","ABNB","MAR","HLT",
            # Energia
            "XOM","CVX","COP","SLB","EOG","PXD","MPC","VLO","PSX","HAL","BKR",
            # Comunicaciones
            "DIS","CMCSA","T","VZ","TMUS","WBD","PARA","SPOT",
            # Industria
            "BA","CAT","GE","HON","UPS","RTX","LMT","DE","MMM","NOC",
            "GD","FDX","CSX","UNP","DAL","UAL","ETN","EMR","ROK","ITW",
            # Consumo basico
            "PG","KO","PEP","WMT","MDLZ","KHC","GIS","CL","MO","PM","KR",
            # Materiales
            "LIN","APD","ECL","NEM","FCX","AA","NUE","DD","DOW","LYB","VMC",
            # REITs
            "AMT","PLD","CCI","EQIX","SPG","O","DLR",
            # Utilities
            "NEE","DUK","SO","AEP","EXC","D","PCG","SRE","WEC"
        ]
    },
    "BR": {
        "name": "Brasil",
        "etf": "EWZ",
        "tickers": [
            "PBR","PBR-A","ITUB","BBD","BSBR","VALE","GGB","SID","ABEV",
            "CIG","ELP","ERJ","BRFS","UGP","SBS","CBD","BAK","TIMB","VIVO",
            "PAGS","STNE","XP","ARCE","SMTO","GFI","SUZ"
        ]
    },
    "CN": {
        "name": "China",
        "etf": "MCHI",
        "tickers": [
            "BABA","JD","BIDU","NTES","VIPS","NIO","LI","XPEV","PDD","FUTU",
            "TCOM","BILI","IQ","TME","YUMC","ZTO","DIDI","LAUR","NOAH","CANG",
            "TIGR","UP","DOYU","HUYA","RLX","MNSO","BZ","FINV","CODA","API",
            "LEGN","ZLAB","BGNE","CAN","CLPS","CIFS","AGMH","AIXI"
        ]
    },
    "DE": {
        "name": "Alemania",
        "etf": "EWG",
        "tickers": [
            "BMWYY","VWAGY","SIEGY","DPSGY","BAYRY","RHHBY","DB","BASFY",
            "DDAIF","DTEGY","ALIZF","MRCYY","SAIGY","AUDVF","CRZBY","HENKY",
            "PMMAF","TKAMY","VOWG","EADSY"
        ]
    },
    "GB": {
        "name": "Reino Unido",
        "etf": "EWU",
        "tickers": [
            "BP","SHEL","HSBC","BCS","LYG","AZN","GSK","DEO","BTI","AZ",
            "VOD","RIO","LNVGY","EXPGY","AVVIY","BRDCY","CMWAY","DGEAF",
            "HBCYF","LLOYF","RBSPF","STANF","ULVR","WPP","BATS"
        ]
    },
    "CA": {
        "name": "Canada",
        "etf": "EWC",
        "tickers": [
            "TD","RY","BMO","BNS","CM","ENB","SU","CVE","CNI","CP",
            "ABX","NTR","WSP","MFC","SLF","POW","FFH","ATD","QSR","SHOP",
            "TRI","CNQ","IMO","HSE","ERF","PD","TOT","L","MRU","EMA",
            "AQN","FTS","H","BCE","T"
        ]
    },
    "JP": {
        "name": "Japon",
        "etf": "EWJ",
        "tickers": [
            "SONY","TM","HMC","NTDOY","MFG","SMFG","MTU","NSANY","KYOCY",
            "FUJIY","HTHIY","ITOCY","MUFG","DSNKY","FANUY","KDDIY","MSBHY",
            "NISMY","PCRFY","SEKEY","SFNXF","SSUMY","TOELY","TOYOF"
        ]
    },
    "FR": {
        "name": "Francia",
        "etf": "EWQ",
        "tickers": [
            "LVMUY","CFRHF","HESAY","TTFNF","BNPQY","CRARY","AIRYY","SNYNF",
            "RCRRF","AXAHY","SGBLY","ENLAY","ORAN","TOTAL","STMEF","DANO",
            "MICHF","PUBGY","VEOEY","HOCPY"
        ]
    },
    "CH": {
        "name": "Suiza",
        "etf": "EWL",
        "tickers": [
            "NVS","RHHBY","NSRGY","UBS","CSGP","ABBN","CFR","GIVN",
            "SCMWY","SGSOY","SHLEF","ZFSVF","ZURVY","GEBN","LOGN","SIKA"
        ]
    },
    "KR": {
        "name": "Corea del Sur",
        "etf": "EWY",
        "tickers": [
            "SSNLF","LPL","HYMTF","HXSCF","KBSTY","SKHYF","LGCLF","LGEAF",
            "SMSN","KRGLY","KSLYY","POSCO","PKX","KB","SHG","HDB"
        ]
    },
    "IN": {
        "name": "India",
        "etf": "INDA",
        "tickers": [
            "INFY","WIT","HDB","IBN","VEDL","MFIN","REDFF","RECON",
            "MBFY","ICLR","AZRE","YTRA","IRCTC","CLOV","IIFL"
        ]
    },
    "AU": {
        "name": "Australia",
        "etf": "EWA",
        "tickers": [
            "BHP","RIO","ANZBY","NABZY","WBCAY","CMWAY","MQBKY","CSLLY",
            "ATLCY","BHPLF","RIOAF","TCTZF","WOVUF","NWSLF","AMCRY"
        ]
    },
    "MX": {
        "name": "Mexico",
        "etf": "EWW",
        "tickers": [
            "AMX","GMEXICOB","FEMSAUBD","BIMBOA","CEMEXCPO",
            "TV","MX","GRUMAB","LABB","OMAB"
        ]
    },
    "ES": {
        "name": "España",
        "etf": "EWP",
        "tickers": [
            "BBVA","SAN","TEF","REP","IBDRY","IDEXY","MDRX",
            "ACGPF","AMDRF","FSDDF","GASNY","NTDOF"
        ]
    },
    "IT": {
        "name": "Italia",
        "etf": "EWI",
        "tickers": [
            "ENEL","ENI","ISP","UCG","LUX","STMEF","PIAGF",
            "FWONA","FCAU","CRZBY","ENIOY","FIADF"
        ]
    },
    "NL": {
        "name": "Paises Bajos",
        "etf": "EWN",
        "tickers": [
            "ASML","PHG","HEIA","INGA","RDSA","NN","AHOLD",
            "AEGOF","AKZOY","NXPLF","WOLFF","RDSAF"
        ]
    },
    "SE": {
        "name": "Suecia",
        "etf": "EWD",
        "tickers": [
            "VOLVY","ATLKY","SWDBY","HNNMY","ERICB",
            "SSAAY","SKFRY","ATCOF","ATCO","VOLAF"
        ]
    },
    "IL": {
        "name": "Israel",
        "etf": "EIS",
        "tickers": [
            "CHKP","NICE","WIX","CYBR","MNDY","GLBE",
            "SMFR","TEVA","SGCL","NVEI","NNDM","NNOX"
        ]
    },
    "HK": {
        "name": "Hong Kong",
        "etf": "EWH",
        "tickers": [
            "BEKE","FINV","KRKR","HKXCF","AAWWF",
            "HSNGF","SWKLY","PNGAY"
        ]
    },
    "TW": {
        "name": "Taiwan",
        "etf": "EWT",
        "tickers": [
            "TSM","ASX","AUO","UMC","SPIL",
            "HISMF","MRVL","ACER","ASUSF"
        ]
    },
    "AR": {
        "name": "Argentina",
        "etf": "ARGT",
        "tickers": [
            "MER","BMA","GGAL","SUPV","CEPU","PAM","TGS","LOMA",
            "IRCP","VALO","CRES","EDN","TECO2","TXAR","ALUA"
        ]
    },
    "CL": {
        "name": "Chile",
        "etf": "ECH",
        "tickers": [
            "LTM","BSAC","BCH","ECL","ENIC","SQM","ANDINA","CCU",
            "CMPC","ENIC","COPEC","ENTEL","FALABELLA"
        ]
    },
    "CO": {
        "name": "Colombia",
        "etf": "GXG",
        "tickers": [
            "CEMIG","CIB","GXG","PFBCOLOM","GRUPOESAL"
        ]
    },
    "ZA": {
        "name": "Sudafrica",
        "etf": "EZA",
        "tickers": [
            "NPN","ANG","GFI","GOLD","ANGPY",
            "SXCL","SAPMY","MTNOY","VODAF"
        ]
    }
}

def main():
    print("Verificando tickers disponibles en Yahoo Finance...")
    print("Esto puede tardar unos minutos...")
    print("")

    valid = {}
    invalid = {}

    for country_code, country_data in ADR_BY_COUNTRY.items():
        print("Verificando: " + country_data["name"])
        valid[country_code] = []
        invalid[country_code] = []

        for ticker in country_data["tickers"]:
            try:
                info = yf.Ticker(ticker).info
                name = info.get("shortName", "")
                sector = info.get("sector", "")
                mkt = info.get("marketCap", 0) or 0
                if name and name != ticker and mkt > 0:
                    valid[country_code].append({
                        "ticker": ticker,
                        "name": name,
                        "sector": sector,
                        "industry": info.get("industry", ""),
                        "marketCap": round(mkt / 1e9, 2)
                    })
                    print("  OK  " + ticker + " - " + name)
                else:
                    invalid[country_code].append(ticker)
                    print("  NO  " + ticker)
            except:
                invalid[country_code].append(ticker)
                print("  ERR " + ticker)

    out_path = os.path.join(os.path.dirname(__file__), "valid_adrs.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"valid": valid, "invalid": invalid}, f, ensure_ascii=False, indent=2)

    print("")
    print("LISTO - Resultado guardado en data/valid_adrs.json")
    total_valid = sum(len(v) for v in valid.values())
    total_invalid = sum(len(v) for v in invalid.values())
    print("Tickers validos:   " + str(total_valid))
    print("Tickers invalidos: " + str(total_invalid))

if __name__ == "__main__":
    main()
