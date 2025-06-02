# Analyseplan / Analysis Plan

## Deskriptive Statistik / Descriptive Statistics
### Frage / Questions:
- **Wie viele Fälle wurden insgesamt beraten?** / **How many cases were advised in total?**
- **Wie viele Frauen, Männer wurden insgesamt beraten?** *(Testung auf Normalverteilung)*  
  **How many women and men were advised in total?** *(Testing for normal distribution)*
- **Welches Durchschnittsalter haben die Befragten in der Gesamtheit?**  
  **What is the average age of respondents overall?*

## Analyse pro Fall / Analysis Per Case
- **Wie viele Telefonate pro Fall im Durchschnitt wurden geführt?**  
  **How many phone calls per case were made on average?**
- **Wie lange dauerte die Telefonie?** *(Dauer der Telefonie = letzter TELHV-Datum – Startdatum)*  
  **How long did the phone calls last?** *(Duration of phone calls = last TELHV date – start date)*
- **Wie häufig wurden Risikofaktoren angegeben?** *(Column P=1)*  
  **How often were risk factors indicated?** *(Column P=1)*

## Mittelwertvergleichsanalyse / Mean Comparison Analysis
### Analyse pro Gruppe Heilungsprozess / Analysis per Healing Process Group:
- **Welches Durchschnittsalter haben die Befragten pro Heilungsprozess?**  
  **What is the average age of respondents per healing process?**  
  - Unterscheidet sich das mittlere Alter pro Gruppe?  
    *Does the average age differ between groups?*
- **Wie viele Kontakte wurden im Mittel pro Heilprozess durchgeführt?**  
  **How many contacts were made on average per healing process?**  
  - Unterscheiden sie sich pro Gruppe signifikant?  
    *Do they differ significantly between groups?*
- **Wie viele Frauen/Männer sind in den Gruppen vertreten?**  
  **How many women/men are represented in the groups?**  
  - Unterscheidet sich die Geschlechterverteilung pro Gruppe?  
    *Does the gender distribution differ per group?*
- **T-Test zum statistischen Mittelwertvergleich für jeden Mittelwertvergleich**  
  **T-test for statistical mean comparison for each mean comparison**

## Regressions- oder Korrelationsanalyse / Regression or Correlation Analysis
- **Gibt es einen Zusammenhang zwischen der Gruppe Heilungsprozess und der Anzahl der Telefonate?**  
  **Is there a correlation between the healing process group and the number of phone calls?**
- **Gibt es einen Zusammenhang zwischen der Gruppe Heilungsprozess und der Dauer der Telefonie?**  
  **Is there a correlation between the healing process group and the duration of the phone calls?**

## Log. Regression / Logistic Regression
### Frage / Question:
- **Hat die Einstufung der einzelnen ICUC-Scores (P/FL/P Status/FL Status) einen Einfluss auf die Einschätzung NBE ja/nein?**  
  **Does the classification of the individual ICUC scores (P/FL/P Status/FL Status) influence the assessment NBE yes/no?**
- **Verändern Alter und Geschlecht und Risikofaktoren die Vorhersage?**  
  **Do age, gender, and risk factors change the prediction?**

### Analyse / Analysis:
- **Logistische Regression** / **Logistic Regression**
  - **Abhängige Variable:** `nbe no (Referenz)/yes (binär)`  
    **Dependent variable:** `nbe no (reference)/yes (binary)`
  - **Unabhängige Variablen:** `P, FL, FL Status, P Status (ordinal), Geschlecht (binär), Alter (metrisch), Risikofaktor (binär)`  
    **Independent variables:** `P, FL, FL Status, P Status (ordinal), Gender (binary), Age (metric), Risk factor (binary)`
  - **Ergebnis:** `Richtung der Vorhersage (Coef), statistische Signifikanz (p), Odds ratio`  
    **Outcome:** `direction of prediction (coefficient), statistical significance (p), odds ratio`
  - **Referenzkategorie:** `NBE No`  
    **Reference category:** `NBE No`