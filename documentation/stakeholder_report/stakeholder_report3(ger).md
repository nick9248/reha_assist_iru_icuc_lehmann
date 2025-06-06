# Mittelwertvergleichsanalyse - Ergebnisbericht
## Step 5: Vergleich der Heilungsprozess-Gruppen

---

### 📋 **Untersuchungsziel**

Diese Analyse untersucht, ob sich Patienten mit unterschiedlichen Heilungsverläufen in wichtigen Merkmalen (Alter, Kontakthäufigkeit, Geschlechterverteilung) signifikant unterscheiden.

---

## 🏥 **Gruppendefinitionen**

Die Patienten wurden basierend auf ihren Status-Angaben (StatusFL und StatusP) über alle Besuche hinweg in drei Gruppen eingeteilt:

### **Gruppe 1: Ohne Stagnation** 
- **Definition**: Patienten, die in allen Besuchen nur "verbessert" (Verbesserung) zeigten
- **Anzahl**: 466 Patienten (37.0%)
- **Interpretation**: Optimaler Heilungsverlauf ohne Rückschläge

### **Gruppe 2: Mit Stagnation**
- **Definition**: Patienten mit mindestens einem "unverändert" (Stagnation), aber keinem "verschlechtert"
- **Anzahl**: 672 Patienten (53.3%)
- **Interpretation**: Heilungsverlauf mit Stillstand, aber ohne Verschlechterung

### **Gruppe 3: Mit Verschlechterung**
- **Definition**: Patienten mit mindestens einem "verschlechtert" in ihren Besuchen
- **Anzahl**: 122 Patienten (9.7%)
- **Interpretation**: Problematischer Heilungsverlauf mit Rückschlägen

**Gesamtstichprobe**: 1.260 Patienten

---

## 🔍 **Datenbereinigung**

### **Ausschlusskriterien**
- **263 Patienten ausgeschlossen** (17.3% der ursprünglichen Stichprobe)
- **Grund**: Fehlende Status-Daten (sowohl StatusFL als auch StatusP leer)
- **Logik**: Wenn beide Status-Spalten fehlen, ist eine Gruppenzuordnung unmöglich
- **Einschlusskriterium**: Mindestens eine verfügbare Status-Angabe (StatusFL oder StatusP)

### **Umgang mit partiell fehlenden Daten**
- Patienten mit nur **einer** fehlenden Status-Spalte wurden **beibehalten**
- Verwendung der verfügbaren Status-Information für Gruppenzuordnung
- **Wissenschaftliche Begründung**: Maximierung der Stichprobengröße bei Erhaltung der Datenintegrität

---

## 📊 **Analyseergebnisse**

### **Fragestellung 1: Altersunterschiede zwischen Gruppen**

![Age Distribution by Healing Process Group](/plot/step5_mean_comparison_20250606_105829/alter_nach_gruppe_boxplot_20250606_105829.png)
*Abbildung 1: Box-Plot der Altersverteilung nach Heilungsprozess-Gruppen*

#### **Ergebnisse:**
- **Gruppe 1 (Ohne Stagnation)**: Durchschnitt 49.3 Jahre (n=420)
- **Gruppe 2 (Mit Stagnation)**: Durchschnitt 51.4 Jahre (n=617)  
- **Gruppe 3 (Mit Verschlechterung)**: Durchschnitt 52.6 Jahre (n=112)

#### **Statistischer Test:**
- **ANOVA**: F=2.732, p=0.0655
- **Ergebnis**: **Keine signifikanten Altersunterschiede** zwischen den Gruppen

#### **Interpretation:**
Das Alter der Patienten beeinflusst den Heilungsverlauf **nicht signifikant**. Obwohl ein leichter Trend zu höherem Alter in problematischeren Heilungsgruppen erkennbar ist, ist dieser Unterschied statistisch nicht bedeutsam.

---

### **Fragestellung 2: Kontakthäufigkeit zwischen Gruppen**

![Contact Count by Healing Process Group](/plot/step5_mean_comparison_20250606_105829/kontakte_nach_gruppe_boxplot_20250606_105829.png)
*Abbildung 2: Box-Plot der Kontaktanzahl nach Heilungsprozess-Gruppen*

#### **Ergebnisse:**
- **Gruppe 1 (Ohne Stagnation)**: Durchschnitt 3.45 Kontakte
- **Gruppe 2 (Mit Stagnation)**: Durchschnitt 4.98 Kontakte
- **Gruppe 3 (Mit Verschlechterung)**: Durchschnitt 5.56 Kontakte

#### **Statistischer Test:**
- **ANOVA**: F=45.427, p<0.001 (hochsignifikant)
- **Post-hoc Tests**:
  - Gruppe 1 vs. 2: **Signifikant** (Differenz: -1.52 Kontakte)
  - Gruppe 1 vs. 3: **Signifikant** (Differenz: -2.10 Kontakte)
  - Gruppe 2 vs. 3: **Nicht signifikant** (nach Korrektur)

#### **Interpretation:**
**Klarer Zusammenhang**: Je problematischer der Heilungsverlauf, desto mehr Kontakte sind erforderlich. Patienten mit Verschlechterung benötigen **61% mehr Kontakte** als Patienten mit optimaler Heilung. Dies zeigt den erhöhten Betreuungsaufwand bei komplizierteren Verläufen.

---

### **Fragestellung 3: Geschlechterverteilung zwischen Gruppen**

![Gender Distribution by Healing Process Group](/plot/step5_mean_comparison_20250606_105829/geschlecht_nach_gruppe_barplot_20250606_105829.png)
*Abbildung 3: Geschlechterverteilung nach Heilungsprozess-Gruppen*

#### **Ergebnisse:**
- **Gruppe 1**: 51.1% männlich, 48.9% weiblich
- **Gruppe 2**: 43.0% männlich, 57.0% weiblich
- **Gruppe 3**: 37.7% männlich, 62.3% weiblich

#### **Statistischer Test:**
- **Chi-Quadrat-Test**: χ²=10.536, p=0.0052
- **Ergebnis**: **Signifikante Geschlechterunterschiede** zwischen den Gruppen

#### **Interpretation:**
Es zeigt sich ein **signifikanter Trend**: Je problematischer der Heilungsverlauf, desto höher ist der Frauenanteil. In der Verschlechterungsgruppe sind fast zwei Drittel (62.3%) der Patienten weiblich, während in der optimalen Heilungsgruppe das Geschlechterverhältnis nahezu ausgeglichen ist.

---

## 🔬 **Warum diese statistischen Tests?**

### **ANOVA statt direkter t-Tests**

**Problem mit multiplen t-Tests:**
- Bei 3 Gruppen wären 3 paarweise t-Tests nötig (1 vs. 2, 1 vs. 3, 2 vs. 3)
- **Fehlerkumulation**: Jeder Test hat 5% Irrtumswahrscheinlichkeit
- Bei 3 Tests steigt die Gesamtfehlerwahrscheinlichkeit auf etwa 15%
- **Risiko**: Falsch-positive Ergebnisse ("Signifikanz durch Zufall")

**Lösung mit ANOVA:**
1. **Erste Stufe**: ANOVA testet, ob **überhaupt** Unterschiede zwischen den Gruppen existieren
2. **Zweite Stufe**: Nur wenn ANOVA signifikant ist → paarweise t-Tests
3. **Korrektur**: Bonferroni-Korrektur für multiple Vergleiche (α = 0.05/3 = 0.017)

**Vorteil:** Kontrollierte Fehlerwahrscheinlichkeit bei maximaler statistischer Power

### **Chi-Quadrat-Test für Geschlechterverteilung**
- **Grund**: Geschlecht ist eine kategoriale Variable (männlich/weiblich)
- **t-Tests ungeeignet**: t-Tests sind nur für kontinuierliche Variablen (wie Alter, Kontakte)
- **Chi-Quadrat**: Speziell für Häufigkeitsvergleiche zwischen Gruppen entwickelt

---

## 🎯 **Zusammenfassung und Handlungsempfehlungen**

### **Zentrale Erkenntnisse:**

1. **Kontakthäufigkeit als Indikator**: Die Anzahl der Patientenkontakte spiegelt klar die Schwere des Heilungsverlaufs wider
2. **Geschlechtsspezifische Unterschiede**: Frauen zeigen häufiger problematische Heilungsverläufe
3. **Alter als Faktor**: Spielt überraschenderweise keine signifikante Rolle

### **Praktische Implikationen:**

1. **Ressourcenplanung**: Patienten mit frühen Anzeichen von Stagnation/Verschlechterung benötigen intensivere Betreuung
2. **Geschlechtsspezifische Betreuung**: Besondere Aufmerksamkeit für weibliche Patienten könnte Heilungsverläufe verbessern
3. **Früherkennung**: Monitoring der ersten Status-Entwicklungen zur Vorhersage des Betreuungsaufwands

---

## 📈 **Datenqualität und Validität**

- **Stichprobengröße**: Ausreichend große Gruppen für reliable statistische Tests
- **Ausschlussrate**: 17.3% aufgrund fehlender Daten (akzeptabel)
- **Testvoraussetzungen**: Alle verwendeten Tests erfüllen ihre statistischen Voraussetzungen
- **Effektstärken**: Gefundene Unterschiede sind nicht nur statistisch, sondern auch praktisch bedeutsam

---

*Erstellt am: 06. Juni 2025*  
*Analyst: Step 5 - Mittelwertvergleichsanalyse*  
*Datenbasis: 1.260 Patienten aus bereinigtem Datensatz*