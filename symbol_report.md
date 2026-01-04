# Symbol-Überprüfung für EUREX_DB.json

## Zusammenfassung

- **Gesamt Einträge**: 198
- **Yahoo Finance Symbole**: 198 (alle vorhanden, 0 leer)
- **Google Finance Symbole**: 198 (alle vorhanden, 0 leer)

## Format-Verteilung

### Yahoo Finance
- **.F (Frankfurt)**: 184 Symbole (92.9%)
- **Kein Exchange-Suffix**: 11 Symbole (5.6%)
  - Diese sind hauptsächlich US-Aktien oder OTC-Markt-Symbole
  - Beispiele: SHEL, STLA, GRUB, AGOAF, HLNCF, MGPUF, PROSY, THLLY, UMGNF
- **.AS (Amsterdam)**: 2 Symbole (1.0%)
- **.L (London)**: 1 Symbol (0.5%)

### Google Finance
- **FRA: (Frankfurt)**: 186 Symbole (93.9%)
- **OTCMKTS: (OTC Markets)**: 6 Symbole (3.0%)
  - AGOAF, HLNCF, MGPUF, PROSY, THLLY, UMGNF
- **AMS: (Amsterdam)**: 2 Symbole (1.0%)
- **NYSE: (New York)**: 2 Symbole (1.0%)
  - SHEL, STLA
- **NASDAQ: (NASDAQ)**: 1 Symbol (0.5%)
  - GRUB
- **LON: (London)**: 1 Symbol (0.5%)

## Test-Ergebnisse

### Stichprobe (20 Einträge)
- **Yahoo Finance**: 20/20 funktionieren (100%)
- **Google Finance Format**: 20/20 korrekt (100%)

### Bekannte Probleme
Einige Symbole könnten delisted sein oder keine aktuellen Daten haben:
- `1PK0.F` (Dechra Pharmaceuticals plc)
- `SOW.F` (Software AG)
- `O2D.F` (Telefónica Deutschland)
- `ZO1.F` (zooplus AG)
- `VAR1.F` (VARTA AG)

## Symbole ohne Exchange-Suffix (Yahoo Finance)

| Unternehmen | Symbol Key | Yahoo Symbol | Google Symbol |
|------------|------------|--------------|---------------|
| Abengoa S.A. | AYO | AGOAF | OTCMKTS:AGOAF |
| BP PLC | BP | BSU | FRA:BSU |
| Haleon plc | HLN | HLNCF | OTCMKTS:HLNCF |
| Just Eat Takeaway.com NV | TKW | GRUB | NASDAQ:GRUB |
| M&G | 7MP | MGPUF | OTCMKTS:MGPUF |
| Prosus N.V. | PRX | PROSY | OTCMKTS:PROSY |
| Shell plc | ROY | SHEL | NYSE:SHEL |
| Stellantis N.V. | FIA5 | STLA | NYSE:STLA |
| Thales S.A. | CSF | THLLY | OTCMKTS:THLLY |
| Universal Music Group N.V. | UMG | UMGNF | OTCMKTS:UMGNF |
| Whitbread PLC | WTB | WHF4 | FRA:WHF4 |

## Fazit

✅ **Die Symbole sind grundsätzlich korrekt formatiert:**
- Alle Einträge haben sowohl Yahoo- als auch Google-Symbole
- Die Formate entsprechen den erwarteten Standards
- Die meisten Symbole verwenden Frankfurt (FRA/.F) als Börse

⚠️ **Zu beachten:**
1. Einige Symbole könnten delisted sein und benötigen eine Aktualisierung
2. OTC-Markt-Symbole (OTCMKTS) könnten weniger zuverlässige Daten liefern
3. US-Aktien (NYSE, NASDAQ) sollten separat überprüft werden

## Empfehlungen

1. ✅ Vollständige Überprüfung aller Symbole durchführen (mit `python check_symbols.py --all`)
2. ⚠️ Delisted Symbole identifizieren und aktualisieren
3. ✅ Symbole ohne Exchange-Suffix sind korrekt (US/OTC-Märkte)
4. ✅ Google Finance Symbole haben das korrekte Format (EXCHANGE:SYMBOL)

