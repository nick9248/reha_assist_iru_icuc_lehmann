# Medical Data Analysis - Plot Documentation

## Project Overview
This document provides detailed explanations for all visualizations generated during the comprehensive medical consultation data analysis. The analysis follows a 6-step pipeline:

1. **Dataset Analysis** - Data exploration and validation
2. **Data Cleaning** - Duplicate removal and data quality fixes  
3. **Descriptive Analysis** - Demographics and basic statistics
4. **Case Analysis** - Call patterns and risk factors
5. **Mean Comparison Analysis** - Group comparisons with statistical tests
6. **Logistic Regression Analysis** - Predictive modeling and correlations

### Plot: Verteilung der Anrufe pro Fall (Distribution of Calls per Case)

**Related Query**: "How many phone calls per case were made on average?"

**Plot Elements**:
- **X-axis**: Number of calls per case (Anzahl der Anrufe pro Fall)
- **Y-axis**: Number of cases (Anzahl der Fälle)
- **Light blue bars**: Frequency distribution showing how many cases had each number of calls
- **Red dashed line**: Average number of calls per case (Durchschnitt: 4.16)
- **Distribution pattern**: Right-skewed distribution with most cases having 1-5 calls

**Results**:
The analysis shows that most cases require relatively few calls. The highest bar is at 3 calls per case (~280 cases), followed by 2 calls (~270 cases) and 4 calls (~205 cases). The average is 4.16 calls per case. The distribution shows a clear right-skewed pattern, with fewer cases requiring many calls (some cases extend to 15+ calls, but these are rare).

**Interpretation**:
Most patient consultations are resolved efficiently with 2-4 phone calls, which represents typical follow-up care. The average of about 4 calls per case suggests that most patients need an initial contact plus 2-3 follow-up calls to complete their care journey. However, some complex cases require extensive follow-up with 10+ calls, though these represent a small minority. This pattern indicates that the consultation system is generally efficient, with most patients receiving appropriate care through a manageable number of contacts.

### Plot: Verteilung der Risikofaktoren bei Patienten (Distribution of Risk Factors in Patients)

**Related Query**: "How often were risk factors indicated?"

**Plot Elements**:
- **X-axis**: Risk factor status (Risikofaktor-Status)
- **Y-axis**: Number of patients (Anzahl der Patienten)
- **Three categories**:
  - **Gray bar**: "Keine Information" (No Information) - 870 patients (57.1%)
  - **Light red bar**: "Ja" (Yes - has risk factors) - 636 patients (41.8%)
  - **Light blue bar**: "Nein" (No - no risk factors) - 17 patients (1.1%)
- **Labels**: Each bar shows both absolute count and percentage

**Results**:
The analysis reveals that risk factor information is missing for more than half of the patients (57.1%). Among patients with documented risk factor status, the vast majority (636 patients, 41.8% of total) have risk factors present, while only 17 patients (1.1% of total) are documented as having no risk factors.

**Interpretation**:
There's a significant data quality issue with risk factor documentation - over half of patients have no recorded risk factor information. Among those with documented status, risk factors are very common (97.5% of documented cases have risk factors vs. 2.5% without). This suggests either that patients seeking consultation typically have underlying health conditions, or there may be a reporting bias where risk factors are more likely to be documented when present. The extremely low number of patients documented as having "no risk factors" indicates that this field may only be completed when risk factors are identified, rather than systematically for all patients.

### Plot: Geschlechterverteilung nach Heilungsprozess-Gruppe (Gender Distribution by Healing Process Group)

**Related Query**: "How many women/men are represented in the groups? Does the gender distribution differ per group?"

**Plot Elements**:
- **X-axis**: Healing process groups (Heilungsprozess-Gruppe)
  - **Gruppe 1**: "Ohne Stagnation" (Without Stagnation) - n=466 patients
  - **Gruppe 2**: "Mit Stagnation" (With Stagnation) - n=670 patients
  - **Gruppe 3**: "Mit Verschlechterung" (With Deterioration) - n=122 patients
- **Y-axis**: Percentage (Prozent)
- **Stacked bar chart elements**:
  - **Light blue sections**: "Männlich" (Male) percentages
  - **Light pink sections**: "Weiblich" (Female) percentages
- **Gender percentages by group**:
  - **Group 1**: 51.1% male, 48.9% female
  - **Group 2**: 43.0% male, 57.0% female  
  - **Group 3**: 37.7% male, 62.3% female
- **Statistical test**: Chi-square test result (Chi²=10.536, p=0.0052)

**Results**:
There is a statistically significant association between gender and healing process groups (Chi²=10.536, p=0.0052). Group 1 (smooth healing) shows a nearly equal gender distribution (51.1% male, 48.9% female). However, as healing outcomes worsen, the proportion of female patients increases: Group 2 (stagnation) has 57.0% female patients, and Group 3 (deterioration) has 62.3% female patients.

**Interpretation**:
Gender appears to be significantly associated with healing outcomes, with women being more likely to experience healing complications. While patients with smooth healing show balanced gender representation, those with stagnation or deterioration are predominantly female (57-62%). This could indicate biological differences in healing responses, different injury patterns between genders, or potentially different healthcare-seeking behaviors. This finding suggests that gender should be considered as a potential risk factor when assessing healing prognosis and developing treatment plans.

### Plot: Kontaktanzahl nach Heilungsprozess-Gruppe (Contact Count by Healing Process Group)

**Related Query**: "How many contacts were made on average per healing process and do they differ significantly between groups?"

**Plot Elements**:
- **X-axis**: Healing process groups (Heilungsprozess-Gruppe)
  - **Gruppe 1**: "Ohne Stagnation" (Without Stagnation) - n=466 patients
  - **Gruppe 2**: "Mit Stagnation" (With Stagnation) - n=672 patients
  - **Gruppe 3**: "Mit Verschlechterung" (With Deterioration) - n=122 patients
- **Y-axis**: Number of contacts (Anzahl Kontakte)
- **Box plot elements**:
  - **Light blue box (Group 1)**: Contact distribution for smooth healing patients
  - **Light green box (Group 2)**: Contact distribution for stagnation patients
  - **Light red box (Group 3)**: Contact distribution for deterioration patients
  - **Orange lines**: Median contacts (approximately 2.5, 4, and 5 respectively)
  - **Whiskers**: Normal range of contact counts
  - **Circles**: Outliers (patients requiring many more contacts than typical)
- **Statistical test**: ANOVA result (F=45.427, p=0.0000)

**Results**:
There is a highly significant difference in contact counts between healing groups (F=45.427, p<0.0001). Group 1 (smooth healing) has the lowest median contact count at approximately 2.5 contacts. Group 2 (stagnation) requires more contacts with a median around 4, while Group 3 (deterioration) needs the most contacts with a median around 5. All groups show outliers requiring 15+ contacts, but the baseline requirement increases with healing complexity.

**Interpretation**:
The number of contacts required is strongly associated with healing outcomes, providing clear evidence that more complex healing trajectories require more intensive follow-up care. Patients with smooth healing typically need only 2-3 contacts, while those experiencing stagnation require about 4 contacts, and patients with deterioration need around 5 contacts on average. This relationship is statistically very strong (p<0.0001), indicating that contact frequency can be both a predictor and consequence of healing complexity. Healthcare resource planning should account for this pattern, with more complex cases requiring proportionally more consultation time and follow-up contacts.

### Plot: Spearman Korrelationsanalyse - Heilungsgruppe vs Kontakte und Dauer (Spearman Correlation Analysis - Healing Groups vs Contacts and Duration)

**Related Query**: "Is there a correlation between healing process group and number/duration of phone calls?"

**Plot Elements**:

**Left Panel - Healing Group vs Contact Count**:
- **X-axis**: Healing groups (Heilungsgruppe)
  - **Ohne Stagnation**: Without stagnation (Group 1)
  - **Mit Stagnation**: With stagnation (Group 2)  
  - **Mit Verschlechterung**: With deterioration (Group 3)
- **Y-axis**: Number of contacts (Anzahl Kontakte), ranging 0-27
- **Blue dots**: Individual patient data points showing contact count for each healing group
- **Red dashed trend line**: Shows positive correlation trend
- **Statistical results**: ρ=0.288, p=0.0000 (highly significant positive correlation)

**Right Panel - Healing Group vs Call Duration**:
- **X-axis**: Same healing groups as left panel
- **Y-axis**: Duration in days (Dauer in Tage), ranging 0-700+ days
- **Green dots**: Individual patient data points showing call duration for each healing group
- **Red trend line**: Shows slight positive correlation trend
- **Statistical results**: ρ=0.210, p=0.0000 (significant positive correlation)

**Results**:
Both analyses reveal statistically significant positive correlations between healing complexity and healthcare utilization:

**Contact Count Correlation (ρ=0.288, p<0.0001)**:
- Moderate positive correlation indicating that patients with more complex healing processes require significantly more contacts
- Group 1 (smooth healing): Most patients need 1-7 contacts, with typical range 2-5 contacts
- Group 2 (stagnation): Broader distribution, many patients requiring 5-15 contacts
- Group 3 (deterioration): Highest contact needs, with some patients requiring 15+ contacts
- The correlation strength (ρ=0.288) indicates a moderate but clinically meaningful relationship

**Duration Correlation (ρ=0.210, p<0.0001)**:
- Weak to moderate positive correlation showing that more complex healing trajectories are associated with longer care periods
- Group 1: Most cases resolved within 0-300 days, with many single-contact cases (0 days duration)
- Group 2: Extended duration range, with many cases lasting 100-400 days
- Group 3: Highest variability, with some cases extending beyond 500-700 days
- The correlation (ρ=0.210) is weaker than contact count but still statistically significant

**Detailed Statistical Interpretation**:
The **highly significant p-values (p<0.0001)** for both correlations provide strong evidence against the null hypothesis of no relationship. The **Spearman correlation** is particularly appropriate here because:
1. The healing groups represent ordinal data (increasing complexity)
2. The relationships may not be perfectly linear
3. There are outliers in both contact and duration data

The **moderate correlation strengths** (0.21-0.29) indicate meaningful clinical relationships while acknowledging that healing group explains only part of the variation in healthcare utilization - other factors (individual patient characteristics, comorbidities, treatment adherence) also influence contact needs and duration.

**Interpretation**:
These correlations provide compelling evidence for a **dose-response relationship** between healing complexity and healthcare resource utilization. As healing trajectories become more complicated (from smooth healing → stagnation → deterioration), patients consistently require more frequent contacts and longer care periods. 

**Clinical Implications**:
1. **Resource Planning**: Healthcare systems can predict resource needs based on early healing trajectory indicators
2. **Risk Stratification**: Patients showing early signs of stagnation or deterioration should be flagged for intensive follow-up protocols
3. **Quality Metrics**: Contact frequency and care duration can serve as objective measures of case complexity
4. **Cost Prediction**: More complex healing cases will require proportionally more resources, allowing for better budget allocation

**Care Management Insights**:
The stronger correlation with contact count (ρ=0.288) compared to duration (ρ=0.210) suggests that **frequency of contact** is more directly related to healing complexity than **total time span**. This indicates that complex cases require more intensive monitoring and intervention rather than simply extending over longer periods. This finding supports proactive, frequent follow-up strategies for patients at risk of complicated healing rather than passive, extended monitoring approaches.

---

## Step 6: Logistic Regression Analysis

### Plot: Logistische Regression - Koeffizienten und Odds Ratios (Logistic Regression - Coefficients and Odds Ratios)

**Related Query**: "Do ICUC scores (P/FL/StatusP/StatusFL) influence NBE assessment? How do age, gender, and risk factors change the prediction?"

**Plot Elements**:

**Left Panel - Coefficients (Koeffizienten)**:
- **X-axis**: Coefficient values (Koeffizient) - shows the log-odds change per unit increase
- **Y-axis**: Predictor variables in German:
  - **Schmerzwerte**: Pain scores (P)
  - **Funktionseinschränkung**: Functional limitation scores (FLScore)
  - **Alter bei Unfall**: Age at accident
  - **Risikofaktor**: Risk factor presence
  - **Schmerz-Status**: Pain status (StatusP_numeric)
  - **Funktions-Status**: Function status (StatusFL_numeric)
  - **Geschlecht (männlich)**: Gender (male)
- **Bar colors**: Red = Significant (p < 0.05), Blue = Not significant
- **Asterisk (*)**: Marks statistically significant predictors
- **Vertical dashed line**: Reference line at coefficient = 0

**Right Panel - Odds Ratios with 95% Confidence Intervals**:
- **X-axis**: Odds Ratio values - shows multiplicative effect on odds of NBE recommendation
- **Y-axis**: Same predictor variables as left panel
- **Bar colors**: Same color coding as coefficients panel
- **Black horizontal lines**: 95% confidence intervals for each odds ratio
- **Black vertical markers**: Lower and upper confidence interval bounds
- **Vertical dashed line**: Reference line at Odds Ratio = 1 (no effect)

**Results**:
The logistic regression model identifies **pain scores (Schmerzwerte)** as the only statistically significant predictor of NBE (follow-up treatment) recommendations. The coefficient for pain scores is approximately -0.5, corresponding to an odds ratio of about 0.6. This means that for each unit increase in pain score, the odds of receiving an NBE recommendation **decrease** by approximately 40% (1 - 0.6 = 0.4). All other predictors (functional limitation, age, risk factors, status variables, and gender) show non-significant associations with NBE recommendations.

**Detailed Statistical Interpretation**:
- **Pain Scores (significant, p < 0.05)**: Higher pain levels are associated with **lower** likelihood of NBE recommendations, which may seem counterintuitive but could indicate that patients with severe pain receive immediate treatment rather than follow-up recommendations
- **Functional Status and Pain Status**: Despite being clinical measures, these status variables do not significantly predict NBE recommendations
- **Age and Gender**: Demographics do not influence NBE recommendation decisions
- **Risk Factors**: The presence of risk factors does not significantly affect the likelihood of receiving follow-up care recommendations
- **Functional Limitation Scores**: While clinically relevant, these scores don't independently predict NBE recommendations in this model

**Interpretation**:
This analysis reveals a paradoxical but clinically meaningful finding: patients with higher pain scores are actually less likely to receive NBE (follow-up care) recommendations. This could indicate several important clinical patterns: (1) patients with severe pain may receive immediate intensive treatment rather than being referred for follow-up care, (2) severe pain cases might be handled through different care pathways, or (3) the NBE recommendations may be more focused on preventive or maintenance care rather than acute pain management. 

The fact that other clinical measures (functional limitations, status assessments) and patient characteristics (age, gender, risk factors) do not significantly predict NBE recommendations suggests that the decision-making process for follow-up care may be more complex than captured by these variables alone, or that pain level serves as the primary clinical decision point. This finding has important implications for standardizing follow-up care protocols and ensuring that all patients who could benefit from continued care receive appropriate recommendations.

---

## Step 5: Mean Comparison Analysis

### Plot: Altersverteilung nach Heilungsprozess-Gruppe (Age Distribution by Healing Process Group)

**Related Query**: "What is the average age of respondents per healing process and does the average age differ between groups?"

**Plot Elements**:
- **X-axis**: Healing process groups (Heilungsprozess-Gruppe)
  - **Gruppe 1**: "Ohne Stagnation" (Without Stagnation) - n=420 patients
  - **Gruppe 2**: "Mit Stagnation" (With Stagnation) - n=617 patients  
  - **Gruppe 3**: "Mit Verschlechterung" (With Deterioration) - n=112 patients
- **Y-axis**: Age in years (Alter in Jahre)
- **Box plot elements**:
  - **Light blue box (Group 1)**: Age distribution for patients with smooth healing
  - **Light green box (Group 2)**: Age distribution for patients with healing stagnation
  - **Light red box (Group 3)**: Age distribution for patients with deterioration
  - **Orange lines**: Median ages (approximately 52, 55, and 54 years respectively)
  - **Whiskers**: Age ranges within normal variation
  - **Circles**: Outliers (unusually young or old patients)
- **Statistical test**: ANOVA result shown (F=2.732, p=0.0655)

**Results**:
The three healing groups show similar age distributions with medians around 52-55 years. Group 1 (smooth healing) has a median age of approximately 52 years, Group 2 (stagnation) around 55 years, and Group 3 (deterioration) around 54 years. The ANOVA test (F=2.732, p=0.0655) indicates no statistically significant difference in age between the healing groups at the 0.05 significance level.

**Interpretation**:
Age does not appear to be a significant factor in determining healing outcomes. All three healing process groups have very similar age distributions, with most patients in their 40s-60s regardless of their healing trajectory. This suggests that factors other than age are more important in determining whether a patient experiences smooth healing, stagnation, or deterioration. The healing process appears to be independent of patient age, which is clinically relevant as it indicates that age alone should not be used to predict healing outcomes.

---

## Step 3: Descriptive Analysis

### Plot: Altersverteilung der Patienten (Age Distribution of Patients)

**Related Query**: "What is the average age of the respondents overall?"

**Plot Elements**:
- **Left Plot - Age Distribution Histogram**:
  - **X-axis**: Age in years (Alter in Jahren)
  - **Y-axis**: Frequency density (Häufigkeitsdichte)
  - **Blue bars**: Observed age distribution of patients
  - **Red line**: Normal distribution overlay for comparison

- **Right Plot - Box Plot**:
  - **Y-axis**: Age in years (Alter in Jahren)
  - **Green box**: Middle 50% of ages (interquartile range)
  - **Red line in box**: Median age (~52-53 years)
  - **Whiskers**: Range of typical values
  - **Circle**: Potential outlier (very young patient)

**Results**:
The analysis shows patient ages ranging from very young (near 0) to elderly (around 85+ years), with most patients being middle-aged adults. The median age appears to be around 52-53 years.

**Interpretation**:
Most patients seeking medical consultation are middle-aged adults in their 50s. While we see patients of all ages from children to elderly, the typical patient is around 52-53 years old. The age distribution is fairly normal (bell-shaped), meaning we have a good representative sample across different age groups.

---

## Step 4: Case Analysis

### Plot: Box-Plot - Anrufdauer pro Fall (Call Duration per Case)

**Related Query**: "How long did the phone calls last (Duration = last date - first date) on average per case?"

**Plot Elements**:
- **Left Plot - All Cases**:
  - **Y-axis**: Duration in days (Dauer in Tagen)
  - **Light blue box**: Shows the middle 50% of call durations for all cases
  - **Red line in box**: Median duration (64.0 days)
  - **Statistics box**: Mean: 78.9 days, Median: 64.0 days, Std: 81.6 days
  - **Whiskers**: Range of typical durations (0 to ~240 days)
  - **Black circles**: Outliers (cases with unusually long durations, up to ~500 days)

- **Right Plot - Multiple Calls Only**:
  - **Y-axis**: Duration in days (Dauer in Tagen)
  - **Light green box**: Shows duration distribution for cases with multiple calls only
  - **Red line in box**: Median duration (75.0 days)
  - **Statistics box**: Mean: 93.8 days, Median: 75.0 days, Std: 80.8 days
  - **Similar outlier pattern**: Some cases extend to ~500 days

**Results**:
The analysis shows that call durations vary significantly. For all cases, the average duration is 78.9 days with a median of 64.0 days. When excluding single-call cases, the average increases to 93.8 days with a median of 75.0 days. Many cases show durations between 0-120 days, but there are notable outliers extending up to 500+ days.

**Interpretation**:
Most patient consultation processes last about 2-3 months (64-75 days), which represents the typical follow-up period. However, there's considerable variation - some patients need only a single call (0 days duration), while others require extended care lasting over a year. The presence of many outliers suggests that certain complex cases require significantly longer monitoring and support periods. When patients need multiple calls, the process typically takes about 2.5 months from first to last contact.

---

## Additional Plots

*[Plots will be added as provided]*

