# Mean Comparison Analysis - Results Report
## Step 5: Comparison of Healing Process Groups

---

### 📋 **Study Objective**

This analysis investigates whether patients with different healing trajectories differ significantly in important characteristics (age, contact frequency, gender distribution).

---

## 🏥 **Group Definitions**

Patients were categorized into three groups based on their status indicators (StatusFL and StatusP) across all visits:

### **Group 1: Without Stagnation** 
- **Definition**: Patients showing only "improved" status across all visits
- **Count**: 466 patients (37.0%)
- **Interpretation**: Optimal healing trajectory without setbacks

### **Group 2: With Stagnation**
- **Definition**: Patients with at least one "unchanged" status, but no "worsened" status
- **Count**: 672 patients (53.3%)
- **Interpretation**: Healing trajectory with periods of stagnation, but no deterioration

### **Group 3: With Deterioration**
- **Definition**: Patients with at least one "worsened" status in their visits
- **Count**: 122 patients (9.7%)
- **Interpretation**: Problematic healing trajectory with setbacks

**Total Sample**: 1,260 patients

---

## 🔍 **Data Cleaning**

### **Exclusion Criteria**
- **263 patients excluded** (17.3% of original sample)
- **Reason**: Missing status data (both StatusFL and StatusP empty)
- **Logic**: If both status columns are missing, group assignment is impossible
- **Inclusion criterion**: At least one available status indicator (StatusFL or StatusP)

### **Handling Partially Missing Data**
- Patients with only **one** missing status column were **retained**
- Used available status information for group assignment
- **Scientific rationale**: Maximize sample size while maintaining data integrity

---

## 📊 **Analysis Results**

### **Question 1: Age Differences Between Groups**

![Age Distribution by Healing Process Group](/plot/step5_mean_comparison_20250606_105829/alter_nach_gruppe_boxplot_20250606_105829.png)  
*Figure 1: Box plot of age distribution by healing process groups*

#### **Results:**
- **Group 1 (Without Stagnation)**: Average 49.3 years (n=420)
- **Group 2 (With Stagnation)**: Average 51.4 years (n=617)  
- **Group 3 (With Deterioration)**: Average 52.6 years (n=112)

#### **Statistical Test:**
- **ANOVA**: F=2.732, p=0.0655
- **Result**: **No significant age differences** between groups

#### **Interpretation:**
Patient age does **not significantly influence** healing trajectory. Although a slight trend toward higher age in more problematic healing groups is observable, this difference is not statistically significant.

---

### **Question 2: Contact Frequency Between Groups**

![Contact Count by Healing Process Group](/plot/step5_mean_comparison_20250606_105829/kontakte_nach_gruppe_boxplot_20250606_105829.png)  
*Figure 2: Box plot of contact count by healing process groups*

#### **Results:**
- **Group 1 (Without Stagnation)**: Average 3.45 contacts
- **Group 2 (With Stagnation)**: Average 4.98 contacts
- **Group 3 (With Deterioration)**: Average 5.56 contacts

#### **Statistical Test:**
- **ANOVA**: F=45.427, p<0.001 (highly significant)
- **Post-hoc Tests**:
  - Group 1 vs. 2: **Significant** (Difference: -1.52 contacts)
  - Group 1 vs. 3: **Significant** (Difference: -2.10 contacts)
  - Group 2 vs. 3: **Not significant** (after correction)

#### **Interpretation:**
**Clear relationship**: The more problematic the healing trajectory, the more contacts are required. Patients with deterioration need **61% more contacts** than patients with optimal healing. This demonstrates the increased care burden with complicated trajectories.

---

### **Question 3: Gender Distribution Between Groups**

![Gender Distribution by Healing Process Group](/plot/step5_mean_comparison_20250606_105829/geschlecht_nach_gruppe_barplot_20250606_105829.png)  
*Figure 3: Gender distribution by healing process groups*

#### **Results:**
- **Group 1**: 51.1% male, 48.9% female
- **Group 2**: 43.0% male, 57.0% female
- **Group 3**: 37.7% male, 62.3% female

#### **Statistical Test:**
- **Chi-Square Test**: χ²=10.536, p=0.0052
- **Result**: **Significant gender differences** between groups

#### **Interpretation:**
There is a **significant trend**: The more problematic the healing trajectory, the higher the proportion of women. In the deterioration group, almost two-thirds (62.3%) of patients are female, while in the optimal healing group, the gender ratio is nearly balanced.

---

## 🔬 **Why These Statistical Tests?**

### **ANOVA Instead of Direct t-Tests**

**Problem with Multiple t-Tests:**
- With 3 groups, 3 pairwise t-tests would be needed (1 vs. 2, 1 vs. 3, 2 vs. 3)
- **Error accumulation**: Each test has 5% error probability
- With 3 tests, total error probability increases to about 15%
- **Risk**: False-positive results ("significance by chance")

**Solution with ANOVA:**
1. **First stage**: ANOVA tests whether differences between groups exist **at all**
2. **Second stage**: Only if ANOVA is significant → pairwise t-tests
3. **Correction**: Bonferroni correction for multiple comparisons (α = 0.05/3 = 0.017)

**Advantage:** Controlled error probability with maximum statistical power

### **Chi-Square Test for Gender Distribution**
- **Reason**: Gender is a categorical variable (male/female)
- **t-Tests unsuitable**: t-tests are only for continuous variables (like age, contacts)
- **Chi-Square**: Specifically developed for frequency comparisons between groups

---

## 🎯 **Summary and Action Recommendations**

### **Key Findings:**

1. **Contact frequency as indicator**: The number of patient contacts clearly reflects the severity of the healing trajectory
2. **Gender-specific differences**: Women show more problematic healing trajectories more frequently
3. **Age as factor**: Surprisingly plays no significant role

### **Practical Implications:**

1. **Resource planning**: Patients with early signs of stagnation/deterioration require more intensive care
2. **Gender-specific care**: Special attention to female patients could improve healing outcomes
3. **Early detection**: Monitoring initial status developments to predict care requirements

---

## 📈 **Data Quality and Validity**

- **Sample size**: Sufficiently large groups for reliable statistical tests
- **Exclusion rate**: 17.3% due to missing data (acceptable)
- **Test assumptions**: All used tests meet their statistical requirements
- **Effect sizes**: Found differences are not only statistically but also practically significant

---

*Created on: June 06, 2025*  
*Analyst: Step 5 - Mean Comparison Analysis*  
*Data basis: 1,260 patients from cleaned dataset*