import pandas as pd

# Beispielhafte Branchen-/Sektor-Tabelle für wichtige europäische Blue-Chip-Indizes
data = [
    # DAX (Deutschland)
    ("ADS.DE", "Adidas AG", "Textiles, Apparel & Luxury Goods", "Consumer Discretionary"),
    ("ALV.DE", "Allianz SE", "Insurance", "Financials"),
    ("BAS.DE", "BASF SE", "Chemicals", "Materials"),
    ("BAYN.DE", "Bayer AG", "Pharmaceuticals", "Health Care"),
    ("BMW.DE", "BMW AG", "Automobiles", "Consumer Discretionary"),
    ("DBK.DE", "Deutsche Bank AG", "Banks", "Financials"),
    ("DTE.DE", "Deutsche Telekom AG", "Telecommunication Services", "Communication Services"),
    ("MRK.DE", "Merck KGaA", "Pharmaceuticals", "Health Care"),
    ("SAP.DE", "SAP SE", "Software", "Information Technology"),
    ("SIE.DE", "Siemens AG", "Industrial Conglomerates", "Industrials"),
    
    # CAC 40 (Frankreich)
    ("OR.PA", "L'Oréal S.A.", "Personal Products", "Consumer Staples"),
    ("MC.PA", "LVMH", "Textiles, Apparel & Luxury Goods", "Consumer Discretionary"),
    ("BN.PA", "Danone S.A.", "Food Products", "Consumer Staples"),
    ("SAN.PA", "Sanofi", "Pharmaceuticals", "Health Care"),
    ("AI.PA", "Air Liquide S.A.", "Chemicals", "Materials"),
    ("GLE.PA", "Société Générale", "Banks", "Financials"),
    
    # FTSE 100 (UK)
    ("VOD.L", "Vodafone Group", "Telecommunication Services", "Communication Services"),
    ("HSBA.L", "HSBC Holdings", "Banks", "Financials"),
    ("ULVR.L", "Unilever plc", "Household Products", "Consumer Staples"),
    ("RIO.L", "Rio Tinto Group", "Metals & Mining", "Materials"),
    ("BP.L", "BP plc", "Oil, Gas & Consumable Fuels", "Energy"),
    
    # SMI (Schweiz)
    ("NESN.SW", "Nestlé S.A.", "Packaged Foods & Meats", "Consumer Staples"),
    ("ROG.SW", "Roche Holding", "Pharmaceuticals", "Health Care"),
    ("NOVN.SW", "Novartis", "Pharmaceuticals", "Health Care"),
    ("UBSG.SW", "UBS Group", "Capital Markets", "Financials"),
    ("CSGN.SW", "Credit Suisse", "Capital Markets", "Financials"),
]

df = pd.DataFrame(data, columns=["Ticker", "Company", "Industry", "Sector"])
import caas_jupyter_tools
caas_jupyter_tools.display_dataframe_to_user("Europäische Blue-Chip Branchenliste", df)
