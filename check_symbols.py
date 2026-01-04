#!/usr/bin/env python3
"""
Script to verify Yahoo Finance and Google Finance symbols from EUREX_DB.json
"""
import json
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

def load_eurex_db():
    """Load EUREX_DB.json"""
    with open('EUREX_DB.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def test_yahoo_symbol(symbol, company_name):
    """Test if Yahoo Finance symbol works"""
    if not symbol or symbol == "":
        return False, "Empty symbol"
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Try to get basic info
        info = ticker.fast_info
        if info is None or info == {}:
            return False, "No fast_info available"
        
        # Try to get historical data
        history = ticker.history(period="5d")
        if history.empty:
            return False, "No historical data"
        
        # Check if we have recent data
        if len(history) == 0:
            return False, "Empty history"
        
        # Get current price
        current_price = ticker.history(period="1d")['Close'].iloc[-1] if not ticker.history(period="1d").empty else None
        
        return True, f"OK - Price: {current_price:.2f}" if current_price else "OK - No current price"
    
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"

def check_google_symbol_format(symbol):
    """Check if Google Finance symbol format looks correct"""
    if not symbol or symbol == "":
        return False, "Empty symbol"
    
    # Google Finance format is typically: EXCHANGE:SYMBOL (e.g., FRA:ADS, NYSE:AAPL)
    if ':' in symbol:
        return True, "Format looks correct"
    else:
        return False, "Format might be incorrect (should be EXCHANGE:SYMBOL)"

def main():
    print("=" * 80)
    print("Überprüfung der Symbole in EUREX_DB.json")
    print("=" * 80)
    print()
    
    # Load data
    data = load_eurex_db()
    
    # Get all entries (excluding 'reverseid')
    entries = {k: v for k, v in data.items() if k != 'reverseid'}
    
    print(f"Gefundene Einträge: {len(entries)}")
    print()
    
    # Statistics
    stats = {
        'total': len(entries),
        'yahoo_ok': 0,
        'yahoo_fail': 0,
        'yahoo_empty': 0,
        'google_format_ok': 0,
        'google_format_fail': 0,
        'google_empty': 0,
    }
    
    # Results storage
    results = []
    
    # Test entries
    import sys
    if '--all' in sys.argv:
        print("Teste ALLE Einträge (dies kann einige Minuten dauern)...")
        sample_entries = list(entries.items())
    else:
        print("Teste zunächst eine Stichprobe von 20 Einträgen...")
        sample_entries = list(entries.items())[:20]
    
    print("-" * 80)
    
    for symbol_key, entry in sample_entries:
        company_name = entry.get('_id', 'Unknown')
        yahoo_symbol = entry.get('yahoo', '')
        google_symbol = entry.get('google', '')
        
        print(f"\n{company_name} ({symbol_key}):")
        print(f"  Yahoo Symbol: {yahoo_symbol}")
        print(f"  Google Symbol: {google_symbol}")
        
        # Test Yahoo
        if yahoo_symbol:
            yahoo_ok, yahoo_msg = test_yahoo_symbol(yahoo_symbol, company_name)
            print(f"  Yahoo Status: {'✓' if yahoo_ok else '✗'} {yahoo_msg}")
            if yahoo_ok:
                stats['yahoo_ok'] += 1
            else:
                stats['yahoo_fail'] += 1
        else:
            print(f"  Yahoo Status: ✗ Empty symbol")
            stats['yahoo_empty'] += 1
        
        # Check Google format
        if google_symbol:
            google_ok, google_msg = check_google_symbol_format(google_symbol)
            print(f"  Google Format: {'✓' if google_ok else '✗'} {google_msg}")
            if google_ok:
                stats['google_format_ok'] += 1
            else:
                stats['google_format_fail'] += 1
        else:
            print(f"  Google Format: ✗ Empty symbol")
            stats['google_empty'] += 1
        
        results.append({
            'company': company_name,
            'symbol_key': symbol_key,
            'yahoo': yahoo_symbol,
            'yahoo_ok': yahoo_ok if yahoo_symbol else False,
            'yahoo_msg': yahoo_msg if yahoo_symbol else 'Empty',
            'google': google_symbol,
            'google_format_ok': google_ok if google_symbol else False,
            'google_msg': google_msg if google_symbol else 'Empty',
        })
        
        # Small delay to avoid rate limiting
        time.sleep(0.3)
        
        # Progress indicator
        if len(results) % 10 == 0:
            print(f"\n  Fortschritt: {len(results)}/{len(sample_entries)} getestet...")
    
    print("\n" + "=" * 80)
    print("Zusammenfassung:")
    print("=" * 80)
    print(f"Gesamt getestet: {len(sample_entries)}")
    print(f"\nYahoo Finance:")
    print(f"  ✓ Funktioniert: {stats['yahoo_ok']} ({stats['yahoo_ok']/len(sample_entries)*100:.1f}%)")
    print(f"  ✗ Fehler: {stats['yahoo_fail']} ({stats['yahoo_fail']/len(sample_entries)*100:.1f}%)")
    print(f"  - Leer: {stats['yahoo_empty']} ({stats['yahoo_empty']/len(sample_entries)*100:.1f}%)")
    print(f"\nGoogle Finance Format:")
    print(f"  ✓ Format OK: {stats['google_format_ok']} ({stats['google_format_ok']/len(sample_entries)*100:.1f}%)")
    print(f"  ✗ Format fraglich: {stats['google_format_fail']} ({stats['google_format_fail']/len(sample_entries)*100:.1f}%)")
    print(f"  - Leer: {stats['google_empty']} ({stats['google_empty']/len(sample_entries)*100:.1f}%)")
    
    # Show problematic entries
    problematic = [r for r in results if not r['yahoo_ok'] or not r['google_format_ok']]
    if problematic:
        print(f"\n⚠️  Problematische Einträge ({len(problematic)}):")
        for r in problematic[:10]:  # Show first 10
            print(f"  - {r['company']}: Yahoo={r['yahoo']} ({r['yahoo_msg']}), Google={r['google']} ({r['google_msg']})")
        if len(problematic) > 10:
            print(f"  ... und {len(problematic) - 10} weitere")
    
    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv('symbol_check_results.csv', index=False)
    print(f"\n✓ Ergebnisse gespeichert in: symbol_check_results.csv")
    
    if '--all' not in sys.argv:
        print("\n" + "=" * 80)
        print("Hinweis: Führen Sie das Skript mit --all aus, um alle Einträge zu testen.")
        print("=" * 80)

if __name__ == '__main__':
    main()

