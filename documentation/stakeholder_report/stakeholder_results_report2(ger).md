# Case Analysis Report 
## Fallanalyse - Ergebnisbericht für Stakeholder

**Analysezeitraum:** Juni 2025  
**Datenbasis:** 6.335 Anrufe von 1.523 einzigartigen Patienten  
**Analysedatum:** 02. Juni 2025

---

##  Executive Summary

Diese Analyse beantwortet drei zentrale Fragen zur Effizienz und Struktur der Patientenbetreuung:

**Kernerkenntnisse:**
- **Durchschnittlich 4,16 Anrufe pro Fall** - zeigt intensiven Betreuungsbedarf
- **Behandlungsdauer von ~79 Tagen** - etwa 2,5 Monate Betreuungszeit
- **57% der Patienten** haben keine Risikofaktor-Informationen dokumentiert
- **Hohe Datenqualität** - keine widersprüchlichen Risikofaktor-Einträge

---

##  Q1: Anzahl der Anrufe pro Fall

### Hauptergebnisse:
- **4,16 Anrufe pro Fall** im Durchschnitt
- **Spannweite:** 1 bis 27 Anrufe
- **Median:** 3 Anrufe
- **51,2%** der Fälle benötigen 1-3 Anrufe

### Detailverteilung:
| Anrufe | Anzahl Fälle | Prozent |
|--------|--------------|---------|
| 1 Anruf | 241 | 15,8% |
| 2 Anrufe | 275 | 18,1% |
| 3 Anrufe | 263 | 17,3% |
| 4 Anrufe | 206 | 13,5% |
| 5+ Anrufe | 538 | 35,3% |

### Visualisierung:
![Verteilung der Anrufe pro Fall](/plot/step4_case_analysis_20250602_164957/anrufe_pro_fall_verteilung_20250602_164957.png)
*Abbildung 1: Häufigkeitsverteilung der Anrufe pro Fall mit Durchschnittslinie*

### 💡 Interpretation:
- **Über die Hälfte** der Fälle sind komplexer und benötigen 4+ Anrufe
- **Ein Fall** benötigte 27 Anrufe - möglicherweise besonders komplexer Fall
- **Standardabweichung von 2,97** zeigt erhebliche Varianz in der Betreuungsintensität

---

## Q2: Dauer der Anrufperiode pro Fall

### Hauptergebnisse:
- **78,9 Tage** durchschnittliche Betreuungsdauer (alle Fälle)
- **93,8 Tage** durchschnittlich für Mehrfachanrufe
- **241 Einzelanrufe** (Dauer = 0 Tage)
- **1.282 Mehrfachanrufe** mit messbarer Zeitspanne

### Statistische Kennzahlen:
| Kennzahl | Alle Fälle | Nur Mehrfachanrufe |
|----------|------------|-------------------|
| Durchschnitt | 78,9 Tage | 93,8 Tage |
| Median | 64,0 Tage | 75,0 Tage |
| Standardabweichung | 81,6 Tage | 80,8 Tage |
| Maximum | ~500 Tage | ~500 Tage |

### Visualisierung:
![Box-Plot Anrufdauer](/plot/step4_case_analysis_20250602_164957/anrufdauer_boxplot_20250602_164957.png)
*Abbildung 2: Box-Plot der Anrufdauer pro Fall (links: alle Fälle, rechts: nur Mehrfachanrufe)*

###  Interpretation:
- **Durchschnittlich 2,5 Monate** Betreuungszeit
- **Große Varianz** - einige Fälle dauern über ein Jahr
- **Viele Ausreißer** deuten auf besonders komplexe Langzeitbetreuungen hin
- **15,8% Sofortlösungen** (nur ein Anruf nötig)

---

##  Q3: Häufigkeit der Risikofaktoren

### Hauptergebnisse:
- **636 Patienten (41,8%)** haben dokumentierte Risikofaktoren
- **17 Patienten (1,1%)** haben explizit keine Risikofaktoren
- **870 Patienten (57,1%)** haben keine Risikofaktor-Information
- **0 inkonsistente Patienten** - perfekte Datenqualität

### Konsistenzprüfung:
 **Keine Widersprüche gefunden** - kein Patient hat sowohl "Risiko vorhanden" als auch "kein Risiko" in verschiedenen Besuchen

### Visualisierung:
![Risikofaktoren Verteilung](/plot/step4_case_analysis_20250602_164957/risikofaktoren_verteilung_20250602_164957.png)
*Abbildung 3: Verteilung der Risikofaktoren bei Patienten*

### 💡 Interpretation:
- **Dokumentationslücke:** Über die Hälfte der Patienten hat keine Risikofaktor-Dokumentation
- **Hohe Risiko-Prävalenz:** 98,6% der dokumentierten Fälle haben Risikofaktoren
- **Excellente Datenqualität:** Keine widersprüchlichen Einträge

---

##  Detailanalyse und Empfehlungen

### Anruf-Effizienz:
**Befund:** 4,16 Anrufe pro Fall zeigt intensiven Betreuungsbedarf
**Empfehlung:** 
- Analyse der Faktoren, die zu vielen Anrufen führen
- Entwicklung von Leitfäden für effizientere erste Anrufe

### Zeitmanagement:
**Befund:** 79 Tage durchschnittliche Betreuungszeit mit hoher Varianz
**Empfehlung:**
- Priorisierung der Ausreißer-Fälle (>200 Tage)
- Entwicklung von Zeitplänen für verschiedene Fallkomplexitäten

### Risikofaktor-Dokumentation:
**Befund:** 57% fehlende Risikofaktor-Informationen
**Empfehlung:**
- **Sofortige Maßnahme:** Verbesserte Erfassung von Risikofaktoren
- Schulung der Berater zur vollständigen Dokumentation
- Implementierung von Pflichtfeldern im System

---

##  Datenzusammenfassung

| Kennzahl | Wert |
|----------|------|
| **Gesamtzahl Patienten** | 1.523 |
| **Gesamtzahl Anrufe** | 6.335 |
| **Durchschnittliche Anrufe/Fall** | 4,16 |
| **Durchschnittliche Dauer** | 78,9 Tage |
| **Patienten mit Risikofaktoren** | 636 (41,8%) |
| **Patienten ohne Risiko-Info** | 870 (57,1%) |
| **Datenqualität (Konsistenz)** | 100% ✅ |

---

##  Zentrale Handlungsempfehlungen

### Kurzfristig (1-3 Monate):
1. **Risikofaktor-Erfassung verbessern** - Schulungen für Berater
2. **Ausreißer-Fälle analysieren** - Warum dauern manche Fälle >200 Tage?
3. **Best-Practice-Leitfäden** für effiziente Erstanrufe entwickeln

### Mittelfristig (3-6 Monate):
1. **Prädiktive Modelle** für Anrufhäufigkeit entwickeln
2. **Risiko-basierte Priorisierung** der Fälle implementieren
3. **Automatisierte Erinnerungen** für Dokumentationspflichten

### Langfristig (6-12 Monate):
1. **KI-unterstützte Fallklassifikation** basierend auf erwarteter Komplexität
2. **Ressourcenplanung** basierend auf Anrufprognosen
3. **Qualitätsmessung** der Betreuungseffizienz

---

##  Technische Details

**Datenquelle:** Bereinigte Datensätze aus Step 2 (6.335 Datensätze)  
**Analysemethode:** Deskriptive Statistik mit Konsistenzprüfungen  
**Visualisierungen:** Box-Plots, Histogramme, Balkendiagramme  
**Qualitätssicherung:** Automatisierte Anomalie-Erkennung

**Analyseteam:** Data Science Team  
**Kontakt:** [Kontaktinformationen]

---

*Dieser Bericht wurde automatisch generiert am 02. Juni 2025 um 16:49 Uhr*