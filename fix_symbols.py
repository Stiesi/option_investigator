#!/usr/bin/env python3
"""
Script to find correct symbols for specific companies
"""
import yfinance as yf
import json

def test_symbol(symbol, company_name):
    """Test if a symbol works"""
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="5d")
        if not history.empty:
            current_price = ticker.history(period="1d")['Close'].iloc[-1] if not ticker.history(period="1d").empty else None
            return True, current_price
        return False, None
    except:
        return False, None

def find_correct_symbols():
    """Find correct symbols for the companies we need to fix"""
    
    companies = {
        'Telefónica Deutschland': {
            'current_yahoo': 'O2D.F',
            'current_google': 'FRA:O2D',
            'alternatives': ['O2D.DE', 'O2D.F', 'O2Dn.DE', 'O2Dn.F']
        },
        'BP PLC': {
            'current_yahoo': 'BSU',
            'current_google': 'FRA:BSU',
            'alternatives': ['BP', 'BP.L', 'BP.F', 'BSU', 'BP.N']
        },
        'British American Tobacco': {
            'current_yahoo': 'BATS.F',
            'current_google': 'FRA:BATS',
            'alternatives': ['BATS', 'BATS.L', 'BATS.F', 'BTI']
        },
        'Shell plc': {
            'current_yahoo': 'SHEL',
            'current_google': 'NYSE:SHEL',
            'alternatives': ['SHEL', 'SHEL.L', 'SHEL.F', 'RDS-A', 'RDS-B', 'RDSA.L', 'RDSB.L']
        },
        'Stellantis N.V.': {
            'current_yahoo': 'STLA',
            'current_google': 'NYSE:STLA',
            'alternatives': ['STLA', 'STLA.MI', 'STLA.PA', 'STLA.F', 'FCAU']
        }
    }
    
    print("=" * 80)
    print("Suche nach korrekten Symbolen")
    print("=" * 80)
    
    results = {}
    
    for company, info in companies.items():
        print(f"\n{company}:")
        print(f"  Aktuell: Yahoo={info['current_yahoo']}, Google={info['current_google']}")
        print(f"  Teste Alternativen...")
        
        working_symbols = []
        for alt in info['alternatives']:
            works, price = test_symbol(alt, company)
            if works:
                working_symbols.append((alt, price))
                print(f"    ✓ {alt}: {price:.2f}" if price else f"    ✓ {alt}: OK")
            else:
                print(f"    ✗ {alt}: Nicht verfügbar")
        
        if working_symbols:
            # Prefer .F or .L for European stocks, or original if US
            best = None
            for sym, price in working_symbols:
                if company in ['Shell plc', 'Stellantis N.V.']:
                    # US stocks - prefer NYSE/NASDAQ
                    if '.' not in sym or sym.endswith('.F'):
                        best = sym
                        break
                else:
                    # European stocks - prefer .F or .L
                    if sym.endswith('.F') or sym.endswith('.L'):
                        best = sym
                        break
            if not best:
                best = working_symbols[0][0]
            
            results[company] = {
                'yahoo': best,
                'google': determine_google_symbol(best),
                'price': next((p for s, p in working_symbols if s == best), None)
            }
            print(f"  → Empfohlen: Yahoo={best}, Google={results[company]['google']}")
        else:
            print(f"  ⚠️  Keine funktionierenden Symbole gefunden!")
            results[company] = None
    
    return results

def determine_google_symbol(yahoo_symbol):
    """Determine Google Finance symbol from Yahoo symbol"""
    if '.' in yahoo_symbol:
        exchange_part = yahoo_symbol.split('.')[1]
        symbol_part = yahoo_symbol.split('.')[0]
        
        exchange_map = {
            'F': 'FRA',
            'L': 'LON',
            'DE': 'FRA',
            'MI': 'BIT',
            'PA': 'EPA',
            'AS': 'AMS',
            'N': 'NYSE'
        }
        
        google_exchange = exchange_map.get(exchange_part, 'FRA')
        return f"{google_exchange}:{symbol_part}"
    else:
        # No exchange suffix - might be US stock
        # Check if it's a known US stock
        us_stocks = {
            'SHEL': 'NYSE:SHEL',
            'STLA': 'NYSE:STLA',
            'BP': 'NYSE:BP',
            'BATS': 'LON:BATS',
            'BTI': 'NYSE:BTI'
        }
        return us_stocks.get(yahoo_symbol, f'NYSE:{yahoo_symbol}')

if __name__ == '__main__':
    results = find_correct_symbols()
    
    print("\n" + "=" * 80)
    print("Zusammenfassung:")
    print("=" * 80)
    for company, result in results.items():
        if result:
            print(f"{company}:")
            print(f"  Yahoo: {result['yahoo']}")
            print(f"  Google: {result['google']}")
            if result['price']:
                print(f"  Preis: {result['price']:.2f}")




