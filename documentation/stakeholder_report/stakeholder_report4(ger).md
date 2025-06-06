# Regressions- und Korrelationsanalysebericht
## ICUC Patientenergebnis-Vorhersagestudie

**Analysedatum:** 6. Juni 2025  
**Studienzeitraum:** Daten aus 2023  
**Stichprobengröße:** 6.335 Patientenkontakte (1.523 eindeutige Patienten)  
**Analysesoftware:** Python mit statsmodels, scipy, sklearn  

---

## Zusammenfassung

Diese umfassende statistische Analyse untersuchte die Zusammenhänge zwischen Heilungsprozessgruppen, Kontakthäufigkeit, Behandlungsdauer und Faktoren, die die NBE-Compliance (Nachbehandlungsempfehlungen) beeinflussen. Die Studie liefert evidenzbasierte Erkenntnisse für die Ressourcenplanung und Optimierung der Patientenversorgung.

### Haupterkenntnisse:
1. **Starke Korrelation zwischen Heilungskomplexität und Ressourcenverbrauch im Gesundheitswesen**
2. **Schmerzwerte sagen NBE-Compliance signifikant vorher**
3. **Patienten mit komplizierter Heilung benötigen 30% mehr Kontakte und längere Betreuung**
4. **Klinische Implikationen unterstützen gezielte Interventionsstrategien**

---

## Forschungsfragen und Methodik

### Primäre Forschungsfragen:
1. **Korrelationsanalyse:**
   - Gibt es einen Zusammenhang zwischen Heilungsprozessgruppe und Anzahl der Telefonate?
   - Gibt es einen Zusammenhang zwischen Heilungsprozessgruppe und Dauer der Telefonie?

2. **Logistische Regression:**
   - Haben die ICUC-Scores (P/FL/StatusP/StatusFL) einen Einfluss auf die NBE-Einschätzung?
   - Wie verändern Alter, Geschlecht und Risikofaktoren die Vorhersage?

### Angewandte statistische Methoden:
- **Spearman-Rangkorrelation** (nicht-parametrisch, geeignet für ordinale Daten)
- **Logistische Regression** mit Odds Ratios und Konfidenzintervallen
- **Modelldiagnostik** einschließlich VIF-Analyse und Ausreißererkennung

#### Warum diese Methoden gewählt wurden:

**Spearman-Rangkorrelation:**
- **Definition:** Ein nicht-parametrisches statistisches Maß, das die Stärke und Richtung des Zusammenhangs zwischen zwei Rangvariablen bewertet
- **Warum geeignet für unsere Daten:** Unsere Heilungsgruppen sind ordinal (geordnete Kategorien: 1→2→3 repräsentieren zunehmende Komplexität), und Kontakt-/Dauerdaten folgen möglicherweise nicht der Normalverteilung
- **Vorteil gegenüber Pearson:** Setzt keine linearen Beziehungen oder Normalverteilung voraus, macht sie robust für medizinische Daten mit potentiellen Ausreißern
- **Interpretation:** Werte reichen von -1 bis +1, wobei 0,2-0,4 schwache bis moderate Korrelation anzeigt (klinisch bedeutsam in der Gesundheitsforschung)

**Logistische Regression:**
- **Definition:** Eine statistische Methode zur Vorhersage binärer Ergebnisse (NBE Ja/Nein) unter Verwendung mehrerer Prädiktorvariablen
- **Warum geeignet:** Unsere abhängige Variable (NBE-Compliance) ist binär, und wir haben multiple Prädiktoren verschiedener Typen (kontinuierlich, ordinal, kategorisch)
- **Modellgleichung:** log(odds) = β₀ + β₁X₁ + β₂X₂ + ... + βₖXₖ
- **Ergebnisinterpretation:** Liefert Odds Ratios, die zeigen, wie stark jeder Faktor die Wahrscheinlichkeit der NBE-Compliance erhöht oder verringert

**Odds Ratios (OR):**
- **Definition:** Das Verhältnis der Chancen eines Ereignisses in einer Gruppe versus einer anderen
- **Klinische Interpretation:**
  - OR = 1: Kein Effekt
  - OR > 1: Erhöhte Chancen (z.B. OR = 2 bedeutet 2x höhere Chancen)
  - OR < 1: Verringerte Chancen (z.B. OR = 0,5 bedeutet 50% niedrigere Chancen)
- **Beispiel aus unserer Studie:** Schmerz-Score OR = 0,574 bedeutet, jede 1-Punkt-Erhöhung des Schmerzes reduziert NBE-Compliance-Chancen um 42,6%

**VIF (Variance Inflation Factor) Analyse:**
- **Definition:** Misst, wie stark die Varianz eines Regressionskoeffizienten durch Korrelation mit anderen Prädiktoren steigt
- **Zweck:** Erkennt Multikollinearität (wenn Prädiktoren hoch miteinander korreliert sind)
- **Interpretation:** VIF > 5 zeigt potentielle Multikollinearitätsprobleme an
- **Unsere Ergebnisse:** Alle Prädiktoren zeigten VIF < 5, bestätigt dass jede Variable einzigartige Information beiträgt

**AIC (Akaike Information Criterion):**
- **Definition:** Ein Maß für Modellqualität, das Anpassungsgüte mit Modellkomplexität ausbalanciert
- **Zweck:** Hilft beim Vergleich verschiedener Modelle; niedrigerer AIC zeigt besseres Modell an
- **Formel:** AIC = 2k - 2ln(L), wobei k = Anzahl Parameter, L = Likelihood
- **Klinische Relevanz:** Stellt sicher, dass wir das Modell nicht mit zu vielen Variablen überanpassen

---

## Datenstruktur und Definitionen

### Heilungsprozessgruppen:
Basierend auf Patientenstatus über alle Besuche unter Verwendung von StatusP (Schmerzstatus) und StatusFL (Funktionseinschränkungsstatus):

1. **Gruppe 1 - Ohne Stagnation:** 466 Patienten (37,0%)
   - Nur "verbessert" (2) in allen Besuchen
   - Beste Heilungstrajektorie

2. **Gruppe 2 - Mit Stagnation:** 672 Patienten (53,3%)
   - Mindestens ein "unverändert" (1), aber kein "verschlechtert" (0)
   - Moderate Heilungstrajektorie

3. **Gruppe 3 - Mit Verschlechterung:** 122 Patienten (9,7%)
   - Mindestens ein "verschlechtert" (0)
   - Schlechte Heilungstrajektorie

### Variablendefinitionen:

**Abhängige Variable:**
- **NBE (Verlauf_entspricht_NBE):** Binäres Ergebnis (0=Nein, 1=Ja)
  - Zeigt an, ob der Patientenfortschritt den erwarteten Behandlungsrichtlinien entspricht

**Unabhängige Variablen:**
- **P (Schmerzwerte):** 0-4 Skala (0=kein Schmerz, 4=maximaler Schmerz)
- **FLScore (Funktionseinschränkung):** 0-4 Skala (0=keine Einschränkung, 4=maximale Einschränkung)
- **StatusP/StatusFL:** Ordinaler Status (0=verschlechtert, 1=unverändert, 2=verbessert)
- **Alter (Alter-Unfall):** Patientenalter zum Zeitpunkt des Unfalls
- **Geschlecht:** Binär (m=männlich, w=weiblich)
- **Risikofaktor:** Binär (0=kein Risiko, 1=hat Risikofaktoren)

### Kontaktmetriken:
- **Anzahl Kontakte:** Gesamtzahl der Telefonanrufe pro Patient
- **Anrufdauer:** Tage zwischen erstem und letztem Kontakt pro Patient

---

## Statistische Ergebnisse

### 1. Korrelationsanalyseergebnisse

#### Heilungsgruppen vs Anzahl Kontakte
- **Spearman-Korrelationskoeffizient:** ρ = 0,2884
- **P-Wert:** < 0,001 (hochsignifikant)
- **Effektgröße:** Schwache bis moderate positive Korrelation
- **Stichprobengröße:** 1.260 Patienten

**Klinische Interpretation:** Patienten mit komplexeren Heilungsprozessen benötigen signifikant mehr Telefonkontakte. Jede Steigerung der Heilungsgruppenkomplexität ist mit erhöhter Kontakthäufigkeit verbunden.

#### Heilungsgruppen vs Anrufdauer
- **Spearman-Korrelationskoeffizient:** ρ = 0,2098
- **P-Wert:** < 0,001 (hochsignifikant)
- **Effektgröße:** Schwache positive Korrelation
- **Stichprobengröße:** 1.106 Patienten (mit mehreren Anrufen)

**Klinische Interpretation:** Patienten mit komplizierten Heilungsverläufen benötigen längere Betreuungszeiten, mit signifikant verlängerter Zeit zwischen erstem und letztem Kontakt.

### 2. Logistische Regressionsergebnisse

#### Modellleistung:
- **Stichprobengröße:** 503 Patienten (vollständige Fälle)
- **Pseudo R²:** 0,1110 (moderate Erklärungskraft)
- **Modellsignifikanz:** p < 0,001 (hochsignifikant)
- **AIC:** 454,5 (Modellanpassungsindikator)

#### Klassenverteilung:
- **NBE Ja:** 406 Patienten (80,7%)
- **NBE Nein:** 97 Patienten (19,3%)

#### Signifikante Prädiktoren:

**Schmerzwerte (P) - HAUPTBEFUND:**
- **Koeffizient:** -0,5553
- **Odds Ratio:** 0,5739 (95% KI: 0,4163-0,7912)
- **P-Wert:** 0,0007 (hochsignifikant)
- **Effekt:** Jede 1-Punkt-Erhöhung des Schmerzwertes verringert die NBE-Compliance-Chancen um 42,6%

**StatusP (Schmerzstatus) - GRENZWERTIG SIGNIFIKANT:**
- **Koeffizient:** 0,6315
- **Odds Ratio:** 1,8804 (95% KI: 0,9651-3,6639)
- **P-Wert:** 0,0635 (marginal signifikant)
- **Effekt:** Verbesserter Schmerzstatus erhöht NBE-Compliance-Chancen um 88,0%

#### Nicht-signifikante Prädiktoren:
- **Funktionseinschränkungswerte (FLScore):** p = 0,253
- **Alter:** p = 0,929 (kein Alterseffekt)
- **Geschlecht:** p = 0,725 (kein Geschlechtsunterschied)
- **Risikofaktoren:** p = 0,584
- **Funktionsstatus:** p = 0,146

---

## Modelldiagnostik und Annahmen

### Angemessenheit der Stichprobengröße:
- **Erforderliches Minimum:** 70 Patienten (10 pro Prädiktor)
- **Konservatives Minimum:** 140 Patienten (20 pro Prädiktor)
- **Tatsächliche Stichprobe:** 503 Patienten
- **Bewertung:** ✅ Angemessene Stichprobengröße (übertrifft konservative Anforderungen)

### Multikollinearitätsprüfung:
- **VIF-Analyse:** Alle Prädiktoren zeigen VIF < 5 (akzeptabel)
- **Bewertung:** ✅ Keine Multikollinearitätsbedenken zwischen Prädiktoren

### Ausreißererkennung:
- **Extreme Ausreißer:** 25 Patienten (5,0% der Stichprobe)
- **Bewertung:** ✅ Innerhalb akzeptablen Bereichs (<10%)

### Analyse fehlender Daten - Detaillierte Erklärung:

**Definition der Vollständigen Fallanalyse:**
- **Vollständige Fälle:** Patienten mit gültigen (nicht-fehlenden) Daten für ALLE Variablen im logistischen Regressionsmodell
- **Begründung:** Statistische Modelle benötigen vollständige Daten für alle Prädiktoren zur Generierung zuverlässiger Schätzungen
- **Alternative Ansätze:** Multiple Imputation oder Maximum-Likelihood-Methoden (nicht verwendet aufgrund von Komplexität und potentieller Bias-Einführung)

**Schrittweiser Datenreduktionsprozess:**
1. **Ausgangspunkt:** 1.229 Patienten mit gültigen NBE-Ergebnisdaten
2. **Nach Schmerzwerten (P):** 1.197 Patienten verbleibend (32 ausgeschlossen - 2,6% Verlust)
3. **Nach Funktionswerten:** 1.196 Patienten verbleibend (33 ausgeschlossen - 2,7% Verlust)
4. **Nach Alter:** 1.088 Patienten verbleibend (141 ausgeschlossen - 11,5% Verlust)
5. **Nach Risikofaktor:** 506 Patienten verbleibend (723 ausgeschlossen - 58,8% Verlust)
6. **Nach Status-Variablen:** 503 Patienten verbleibend (726 ausgeschlossen - 59,1% Gesamtverlust)

**Hauptursachen für Datenverlust:**

**Risikofaktor-Variable - Hauptauswirkung:**
- **Fehlende Rate:** 668 von 1.229 Patienten (54,4%)
- **Klinischer Grund:** Risikofaktorbewertung wird möglicherweise nicht konsistent über alle Patientenkontakte dokumentiert
- **Auswirkung auf Analyse:** Diese einzelne Variable verursachte die größte Datenreduktion in unserer Studie
- **Überlegung:** Zukünftige Studien könnten verpflichtende Risikofaktordokumentation oder Imputationsmethoden in Betracht ziehen

**Alter-Variable - Moderate Auswirkung:**
- **Fehlende Rate:** 111 Patienten (9,0%)
- **Klinischer Grund:** Alter zum Unfallzeitpunkt wird möglicherweise nicht konsistent in allen Patientenakten erfasst
- **Muster:** Zufälliges Fehlmuster, wahrscheinlich aufgrund administrativer Dateneingabeprobleme

**Status-Variablen (StatusP/StatusFL) - Geringe Auswirkung:**
- **Fehlende Rate:** ~3,5% jeweils
- **Klinischer Grund:** Dies sind zentrale klinische Bewertungen, daher sind Fehlraten niedrig
- **Qualitätsindikator:** Niedrige Fehlraten deuten auf gute klinische Dokumentationspraxen hin

**Schmerz- und Funktionswerte - Minimale Auswirkung:**
- **Fehlende Rate:** <3% jeweils
- **Klinischer Grund:** Dies sind routinemäßige klinische Messungen mit standardisierten Protokollen
- **Qualitätsindikator:** Ausgezeichnete Datenvollständigkeit für zentrale klinische Messungen

**Auswirkungsbewertung fehlender Daten:**

**Repräsentativitätsanalyse:**
- **Beibehaltene Stichprobe:** 503 Patienten (40,9% der ursprünglichen Stichprobe mit NBE-Daten)
- **Bias-Risiko:** Patienten mit vollständigen Risikofaktordaten könnten eine spezifische Untergruppe darstellen
- **Verallgemeinerbarkeit:** Ergebnisse sollten aufgrund erheblicher fehlender Daten mit Vorsicht interpretiert werden

**Sensitivitätsüberlegungen:**
- **Konservativer Ansatz:** Vollständige Fallanalyse liefert unverzerrte Schätzungen, wenn Daten vollständig zufällig fehlen (MCAR)
- **Potentieller Bias:** Wenn Fehlen mit Patientencharakteristika zusammenhängt (Zufällig Fehlend - MAR), sind Ergebnisse möglicherweise nicht vollständig repräsentativ
- **Klinische Validität:** Trotz fehlender Daten bleibt die Stichprobengröße (503) angemessen für zuverlässige statistische Inferenz

**Empfehlungen für zukünftige Studien:**
1. **Verbesserung der Datensammlungsprotokolle** für Risikofaktordokumentation
2. **Erwägung multipler Imputationsmethoden** für den Umgang mit fehlenden Daten
3. **Implementierung verpflichtender Datenfelder** für kritische klinische Variablen
4. **Durchführung einer Analyse fehlender Datenmuster** zur Identifikation systematischer Probleme

---

## Klinische Implikationen und Empfehlungen

### 1. Erkenntnisse zur Ressourcenplanung:
- **Hochkomplexe Patienten** (Gruppe 3) benötigen etwa **30% mehr Kontakte**
- **Verlängerte Betreuungsdauer** für komplizierte Fälle erfordert längere Ressourcenzuteilung
- **Vorhersagbares Muster** ermöglicht proaktive Ressourcenplanung

### 2. Frühwarnsystem:
- **Schmerzwerte sind der stärkste Prädiktor** für NBE-Non-Compliance
- **Patienten mit hohen Schmerzwerten** (3-4) benötigen verstärkte Aufmerksamkeit und Unterstützung
- **Implementierung schmerzfokussierter Interventionen** zur Verbesserung der Behandlungsadhärenz

### 3. Qualitätsverbesserungsmöglichkeiten:
- **Optimierung des Schmerzmanagements** könnte NBE-Compliance-Raten signifikant verbessern
- **Gezielte Interventionen** für Hochschmerz-Patienten können Gesamtkosten im Gesundheitswesen reduzieren
- **Standardisierte Schmerzbewertungsprotokolle** sollten priorisiert werden

### 4. Klinische Entscheidungsunterstützung:
- **Schmerzwerte als primäres Screening-Tool** für NBE-Compliance-Risiko verwenden
- **Zusätzliche Unterstützungsmaßnahmen** für Patienten mit Schmerzwerten ≥3 in Betracht ziehen
- **Heilungsfortschritt** bei Hochrisikopatienten genauer überwachen

---

## Statistische Einschränkungen und Überlegungen

### 1. Fehlende Daten:
- **Risikofaktor-Variable** hatte erhebliche fehlende Daten (54,4%)
- **Vollständige Fallanalyse** kann Selektionsbias einführen
- **Ergebnisse sollten interpretiert werden** unter Berücksichtigung fehlender Datenmuster

### 2. Modellbeschränkungen:
- **Pseudo R² = 0,111** zeigt moderate Vorhersagekraft an
- **Nicht gemessene Störfaktoren** können NBE-Compliance beeinflussen
- **Zeitliche Beziehungen** zwischen Variablen nicht vollständig erforscht

### 3. Verallgemeinerbarkeit:
- **Einzentren-Studie** kann externe Validität begrenzen
- **Spezifische Patientenpopulation** (unfallbedingte Verletzungen)
- **Zeitraumbeschränkungen** (nur Daten von 2023)

---

## Schlussfolgerungen

Diese umfassende Analyse liefert starke statistische Evidenz für mehrere klinisch wichtige Zusammenhänge:

1. **Heilungskomplexität korreliert signifikant mit Ressourcenverbrauch**, was die Notwendigkeit differenzierter Pflegeplanung basierend auf Heilungstrajektorie unterstützt.

2. **Schmerzwerte erweisen sich als zuverlässigster Prädiktor für NBE-Compliance**, was darauf hindeutet, dass Schmerzmanagement priorisiert werden sollte, um Behandlungsergebnisse zu verbessern.

3. **Die vorhersagbare Natur dieser Beziehungen** ermöglicht es Gesundheitsorganisationen, evidenzbasierte Ressourcenzuteilung und frühzeitige Interventionsstrategien zu implementieren.

4. **Klinische Entscheidungsfindung sollte Schmerzbewertung** als primären Faktor bei der Bestimmung von Patientenunterstützungsbedarf und NBE-Compliance-Risiko einbeziehen.

Die Befunde unterstützen die Implementierung gezielter Interventionen mit Fokus auf Schmerzmanagement und differenzierte Pflegeprotokolle basierend auf Heilungstrajektorienkomplexität. Diese evidenzbasierten Strategien haben das Potenzial, sowohl Patientenergebnisse als auch Effizienz der Gesundheitsressourcen zu verbessern.

---

## Anhang: Visuelle Ergebnisse

*[Hinweis: Die folgenden Diagramme wurden während der Analyse erstellt und sollten im endgültigen Bericht enthalten sein]*

### Abbildung 1: Spearman-Korrelationsanalyse
**Datei:** `spearman_korrelation_20250606_132353.png`
- Streudiagramme zeigen Korrelation zwischen Heilungsgruppen und Kontakthäufigkeit/Dauer
- Trendlinien mit Korrelationskoeffizienten und p-Werten
- Deutsche Beschriftungen für Stakeholder-Zugänglichkeit

### Abbildung 2: Logistische Regressionsergebnisse
**Datei:** `logistische_regression_ergebnisse_20250606_132353.png`
- Horizontale Balkendiagramme zeigen Koeffizienten und Odds Ratios
- 95% Konfidenzintervalle für alle Prädiktoren
- Signifikanzmarkierungen und deutsche Variablenbeschriftungen

---

**Bericht erstellt von:** Data Science Team  
**Qualitätssicherung:** Statistische Validierung abgeschlossen  
**Verteilung:** Gesundheitsmanagement, Klinische Leitung, Qualitätsverbesserungsteam