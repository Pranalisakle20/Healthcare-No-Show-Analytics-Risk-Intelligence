# 🏥 Healthcare Appointment No-Show Analytics & AI Risk Intelligence

**Author:** [Pranali Sakle](https://www.linkedin.com/in/pranali-sakle-892b7b262)  
**Tools:** SQL (SQLite/PostgreSQL), Python (Scikit-Learn, Pandas), Power BI Desktop, DAX  

![Executive Dashboard Preview](powerbi/dashboard_preview.png)

---

## 📌 Project Overview

Missed medical appointments cost healthcare organizations billions of dollars annually, lead to underutilized clinical staff, and delay necessary patient care. This project delivers an **end-to-end data analytics and machine learning solution** that uncovers behavioral default drivers, quantifies financial loss, predicts appointment abandonment risk prior to consultation, and empowers clinical operations through an interactive **Power BI Executive Command Center**.

The models are developed on the Kaggle Medical Appointment No-Shows dataset (~110,000 historical records) and operationalized across a 5,000-appointment stratified cohort for real-time risk intelligence.

---

## 🏗️ Repository Architecture

```text
healthcare_Noshow_analytics_endtoend_Project/
├── data/
│   ├── sample_cleaned_appointments.csv           # Baseline cleaned appointment records
│   └── appointments_with_ai_predictions.csv      # Records enriched with ML risk probabilities & tiers
├── models/
│   └── best_healthcare_no_show_model.joblib      # Serialized Scikit-learn Pipeline (ColumnTransformer + Model)
├── powerbi/
│   ├── healthcare_dashboard.pbix                 # Production 1-page interactive executive command center
│   └── dashboard_preview.png                     # High-res dashboard visual asset for presentation
├── sql/
│   ├── healthcare_queries.sql                    # Production DDL, feature views & analytical aggregations
│   └── healthcare.db                             # Relational SQLite database
├── src/
│   └── healthcare_pipeline.py                    # Modular CLI Python ETL & ML training pipeline
├── Healthcare_Analytics_Pipeline.ipynb           # Executed end-to-end Jupyter notebook (EDA, SQL, ML)
├── .gitignore                                    # Git cache and temporary artifact exclusions
└── README.md
```

### 🛠️ Technology Stack

* **Database & Data Modeling:** Relational SQL (DDL, transformation views, comorbidity aggregation, lead-time segmentation)
* **Data Science & Machine Learning:** Python (pandas, numpy, scikit-learn, joblib, matplotlib, seaborn)
* **Business Intelligence & Reporting:** Microsoft Power BI Desktop (DAX measure engineering, semantic color formatting, dynamic operational worklists)

---

## 📊 Executive Dashboard Architecture

The Power BI dashboard consolidates high-level metrics, behavioral root causes, and proactive clinic workflows into a single command center:

### 1. Executive KPI Cards
* **Total Bookings (5,000):** Stratified validation cohort representing operational appointment throughput.
* **No-Show Rate (17.94%):** Clinic baseline failure-to-attend rate (897 total missed appointments).
* **AI High Risk Visits (203):** Appointments flagged by the model having a severe risk probability ($\ge 35\%$), representing 4.06% of clinic volume.
* **Financial Loss ($76K):** Direct unrealized revenue evaluated at an industry benchmark of **$85 per missed consultation slot** ($897 \times \$85 = \$76,245$).

### 2. Analytical Intelligence Layer
* **AI Risk Tiers (Donut Chart):** Segments patient volume into operational risk brackets:
  * `Low Risk (< 20%)`: **25.44%** (1,272 visits) — Standard automated reminder schedule.
  * `Medium Risk (20% – 34%)`: **70.50%** (3,525 visits) — Standard reminder + multi-channel digital nudge.
  * `High Risk (≥ 35%)`: **4.06%** (203 visits) — Active clinical intervention & candidate for targeted double-booking.
* **Waiting Time vs. No-Show Rate (Binned Column Chart):**
  * Same Day: **11.09%** No-Show Rate vs. **88.91%** Show Rate
  * 1–3 Days: **11.29%** No-Show Rate vs. **88.71%** Show Rate
  * 4–7 Days: **16.00%** No-Show Rate vs. **84.00%** Show Rate
  * 8–14 Days: **19.00%** No-Show Rate vs. **81.00%** Show Rate
  * 15+ Days: **28.60%** No-Show Rate vs. **71.40%** Show Rate
* **SMS Reminder Impact (Proportion Analysis):**
  * Patients receiving automated SMS alerts achieved an **84.48%** show rate (15.52% no-show) compared to an **80.73%** show rate (19.27% no-show) for patients without reminders—a **3.75% absolute reduction** in appointment defaults.

### 3. Operational Intervention Worklist
* A tabular patient queue sorted descending by AI Risk Probability (`91.5%`, `91.3%`, `90.3%`, etc.) displaying patient age, lead days, clinical comorbidities (hypertension, diabetes), and SMS dispatch status.
* Centered status badges identify immediate clinic actions (`Prioritize`) for schedule re-confirmation and planned overbooking.

---

## 🧠 Machine Learning Modeling & Benchmarking

To address class imbalance (17.94% positive no-show class), all pipelines utilized stratified splitting and balanced class weighting:

* **Preprocessing:** Scikit-learn `ColumnTransformer` with `StandardScaler` for numeric features (`age`, `lead_days`, `scholarship`, `hypertension`, `diabetes`, `alcoholism`, `handicap`, `sms_received`, `comorbidity_count`) and `OneHotEncoder(handle_unknown='ignore')` for categorical features (`gender`, `appointment_weekday`, `age_group`, `lead_time_bucket`).
* **Benchmark Evaluation:**
  | Model | ROC-AUC | F1-Score | Accuracy |
  | :--- | :---: | :---: | :---: |
  | **Logistic Regression (Class-Weighted)** | **0.6545** | **0.3633** | **0.6110** |
  | Gradient Boosting Classifier | 0.5881 | 0.0498 | 0.8090 |
  | Random Forest Classifier | 0.5544 | 0.1714 | 0.7680 |

The highest-performing model pipeline was serialized to `models/best_healthcare_no_show_model.joblib` and used to enrich appointments with continuous probability scores and risk tiers (`data/appointments_with_ai_predictions.csv`).

---

## 🗄️ Relational SQL Backend

The SQL implementation (`sql/healthcare_queries.sql` and `sql/healthcare.db`) models data transformations and aggregations:

1. **Schema DDL & Staging:** Structured `appointments_staging` table schema.
2. **Feature Engineering View (`v_healthcare_appointments_cleaned`):**
   * Normalizes schedule and appointment timestamps.
   * Derives `lead_days` ($\max(0, \text{appointment\_date} - \text{scheduled\_date})$).
   * Categorizes lead time (`Same Day`, `Short Notice (1-3 d)`, `Medium Notice (4-14 d)`, `Long Notice (>14 d)`).
   * Bins age demographics (`Child`, `Adolescent`, `Young Adult`, `Middle-Aged`, `Senior`).
   * Computes additive patient comorbidity scores (`hypertension + diabetes + alcoholism + handcap`).
3. **Analytical Aggregations:** Generates summary metrics for SMS reminder efficacy, lead time default curves, comorbidity risk grids, and high-volume geographic defaults across neighborhoods.

---

## 📈 Key Clinical & Business Findings

1. **Lead Time is the Dominant Behavioral Driver:** Default rates remain steady (~11%) within 3 days of scheduling but climb by **158%** to **28.6%** when lead times extend past two weeks.
2. **SMS Reminders Drive Significant Attendance Gains:** Automated reminders lower no-shows by ~3.75%, preserving thousands of clinical hours across high-volume health systems.
3. **Targeted Overbooking Strategy:** Instead of uniform overbooking (which causes doctor burnout and waiting-room overcrowding), clinic staff can leverage the **AI Risk Tier** to only double-book slots allocated to the top 4% high-risk cohort.

---

## 🚀 How to Run the Project Locally

### 1. Environment Setup
```bash
git clone https://github.com/Pranalisakle20/Healthcare-NoShow-Analytics-Risk-Intelligence.git
cd Healthcare-NoShow-Analytics-Risk-Intelligence
pip install pandas numpy scikit-learn joblib matplotlib seaborn
```
*(Remember to replace `<your-username>` with your GitHub username when sharing the clone command).*

### 2. Run the Python Pipeline
```bash
python src/healthcare_pipeline.py data/sample_cleaned_appointments.csv
```

### 3. Inspect Interactive Notebook & SQL
* Open `Healthcare_Analytics_Pipeline.ipynb` in Jupyter Notebook, VS Code, or Google Colab.
* Connect to `sql/healthcare.db` using SQLite CLI, DB Browser for SQLite, or execute `sql/healthcare_queries.sql`.

### 4. Open Power BI Dashboard
* Launch **Power BI Desktop**.
* Open `powerbi/healthcare_dashboard.pbix` to interact with slicers (`Gender`, `Age Group`, `Neighbourhood`) and drill into risk tiers.