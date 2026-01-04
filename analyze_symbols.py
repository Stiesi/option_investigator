#!/usr/bin/env python3
"""
Quick analysis of symbols in EUREX_DB.json
"""
import json

def load_eurex_db():
    """Load EUREX_DB.json"""
    with open('EUREX_DB.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    data = load_eurex_db()
    entries = {k: v for k, v in data.items() if k != 'reverseid'}
    
    print("=" * 80)
    print("Analyse der Symbole in EUREX_DB.json")
    print("=" * 80)
    print(f"\nGesamt Einträge: {len(entries)}")
    
    # Check for empty symbols
    yahoo_empty = []
    google_empty = []
    yahoo_symbols = {}
    google_symbols = {}
    
    for symbol_key, entry in entries.items():
        company = entry.get('_id', 'Unknown')
        yahoo = entry.get('yahoo', '')
        google = entry.get('google', '')
        
        if not yahoo or yahoo == "":
            yahoo_empty.append((company, symbol_key))
        else:
            yahoo_symbols[symbol_key] = yahoo
        
        if not google or google == "":
            google_empty.append((company, symbol_key))
        else:
            google_symbols[symbol_key] = google
    
    print(f"\nYahoo Finance Symbole:")
    print(f"  Gesamt: {len(yahoo_symbols)}")
    print(f"  Leer: {len(yahoo_empty)}")
    if yahoo_empty:
        print(f"\n  Leere Yahoo Symbole:")
        for company, key in yahoo_empty[:10]:
            print(f"    - {company} ({key})")
        if len(yahoo_empty) > 10:
            print(f"    ... und {len(yahoo_empty) - 10} weitere")
    
    print(f"\nGoogle Finance Symbole:")
    print(f"  Gesamt: {len(google_symbols)}")
    print(f"  Leer: {len(google_empty)}")
    if google_empty:
        print(f"\n  Leere Google Symbole:")
        for company, key in google_empty[:10]:
            print(f"    - {company} ({key})")
        if len(google_empty) > 10:
            print(f"    ... und {len(google_empty) - 10} weitere")
    
    # Check symbol formats
    print(f"\n" + "=" * 80)
    print("Format-Analyse:")
    print("=" * 80)
    
    # Yahoo formats
    yahoo_formats = {}
    for symbol in yahoo_symbols.values():
        if '.' in symbol:
            exchange = symbol.split('.')[1]
            yahoo_formats[exchange] = yahoo_formats.get(exchange, 0) + 1
        else:
            yahoo_formats['NO_EXCHANGE'] = yahoo_formats.get('NO_EXCHANGE', 0) + 1
    
    print(f"\nYahoo Finance Format-Verteilung:")
    for exchange, count in sorted(yahoo_formats.items(), key=lambda x: -x[1]):
        print(f"  {exchange}: {count}")
    
    # Google formats
    google_formats = {}
    for symbol in google_symbols.values():
        if ':' in symbol:
            exchange = symbol.split(':')[0]
            google_formats[exchange] = google_formats.get(exchange, 0) + 1
        else:
            google_formats['NO_EXCHANGE'] = google_formats.get('NO_EXCHANGE', 0) + 1
    
    print(f"\nGoogle Finance Format-Verteilung:")
    for exchange, count in sorted(google_formats.items(), key=lambda x: -x[1]):
        print(f"  {exchange}: {count}")
    
    # Check for potential issues
    print(f"\n" + "=" * 80)
    print("Potenzielle Probleme:")
    print("=" * 80)
    
    issues = []
    for symbol_key, entry in entries.items():
        company = entry.get('_id', 'Unknown')
        yahoo = entry.get('yahoo', '')
        google = entry.get('google', '')
        
        # Check if Yahoo symbol doesn't have .F (Frankfurt) but should
        if yahoo and '.' not in yahoo and symbol_key in ['SOW', 'O2D', 'ZO1', 'VAR1']:
            issues.append(f"{company}: Yahoo Symbol '{yahoo}' hat kein Exchange-Suffix")
        
        # Check if Google symbol format is wrong
        if google and ':' not in google:
            issues.append(f"{company}: Google Symbol '{google}' hat falsches Format (sollte EXCHANGE:SYMBOL sein)")
    
    if issues:
        print(f"\nGefundene Probleme ({len(issues)}):")
        for issue in issues[:20]:
            print(f"  - {issue}")
        if len(issues) > 20:
            print(f"  ... und {len(issues) - 20} weitere")
    else:
        print("\nKeine offensichtlichen Format-Probleme gefunden.")

if __name__ == '__main__':
    main()




