#!/usr/bin/env python3
"""
=============================================================================
End-to-End Healthcare Analytics & No-Show Prediction Pipeline
Dataset: Medical Appointment No Shows (Kaggle - Joni Arroba)
Author: Data Analytics Engineering Portfolio Project
=============================================================================
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, f1_score, accuracy_score
import joblib

def load_and_clean_data(file_path_or_df):
    if isinstance(file_path_or_df, str):
        df = pd.read_csv(file_path_or_df)
    else:
        df = file_path_or_df.copy()

    # Standardize column headers
    df.columns = [c.strip().replace('-', '_').replace(' ', '_').lower() for c in df.columns]
    rename_dict = {
        'patientid': 'patient_id',
        'appointmentid': 'appointment_id',
        'scheduledday': 'scheduled_day',
        'appointmentday': 'appointment_day',
        'hipertension': 'hypertension',
        'handcap': 'handicap'
    }
    df = df.rename(columns=rename_dict)

    # Convert timestamps
    df['scheduled_day'] = pd.to_datetime(df['scheduled_day'])
    df['appointment_day'] = pd.to_datetime(df['appointment_day'])

    # Data Quality Rules
    df = df[(df['age'] >= 0) & (df['age'] <= 115)].copy()
    df['scheduled_date'] = df['scheduled_day'].dt.normalize()
    df['appointment_date'] = df['appointment_day'].dt.normalize()
    df['lead_days'] = (df['appointment_date'] - df['scheduled_date']).dt.days
    df = df[df['lead_days'] >= 0].copy()

    # Target variable encoding (No-show: 'Yes' = 1, 'No' = 0)
    df['target'] = (df['no_show'].str.strip().str.lower() == 'yes').astype(int)

    return df

def feature_engineering(df):
    df = df.copy()
    df['appointment_weekday'] = df['appointment_day'].dt.day_name()
    
    bins = [-1, 0, 3, 7, 15, 30, 999]
    labels = ['Same Day', '1-3 Days', '4-7 Days', '8-15 Days', '16-30 Days', '30+ Days']
    df['lead_time_bucket'] = pd.cut(df['lead_days'], bins=bins, labels=labels)

    age_bins = [-1, 12, 25, 45, 65, 120]
    age_labels = ['Child (0-12)', 'Youth (13-25)', 'Adult (26-45)', 'Middle-Aged (46-65)', 'Senior (65+)']
    df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)

    df['comorbidity_count'] = (
        df['hypertension'] + 
        df['diabetes'] + 
        df['alcoholism'] + 
        (df['handicap'] > 0).astype(int)
    )

    return df

def train_predictive_models(df):
    feature_cols_num = ['age', 'lead_days', 'scholarship', 'hypertension', 'diabetes', 
                        'alcoholism', 'handicap', 'sms_received', 'comorbidity_count']
    feature_cols_cat = ['gender', 'appointment_weekday', 'age_group', 'lead_time_bucket']

    X = df[feature_cols_num + feature_cols_cat].copy()
    y = df['target'].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    num_transformer = Pipeline(steps=[('scaler', StandardScaler())])
    cat_transformer = Pipeline(steps=[('encoder', OneHotEncoder(handle_unknown='ignore'))])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_transformer, feature_cols_num),
            ('cat', cat_transformer, feature_cols_cat)
        ]
    )

    models = {
        "Logistic Regression": LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=12, class_weight='balanced', random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    }

    results = {}
    best_model = None
    best_roc_auc = 0.0

    print("=================== MODEL EVALUATION RESULTS ===================")
    for name, clf in models.items():
        pipe = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', clf)])
        pipe.fit(X_train, y_train)

        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]

        roc = roc_auc_score(y_test, y_prob)
        f1 = f1_score(y_test, y_pred)
        acc = accuracy_score(y_test, y_pred)

        results[name] = {"ROC-AUC": roc, "F1-Score": f1, "Accuracy": acc}
        print(f"[{name}] AUC: {roc:.4f} | F1: {f1:.4f} | Accuracy: {acc:.4f}")

        if roc > best_roc_auc:
            best_roc_auc = roc
            best_model = pipe

    os.makedirs("models", exist_ok=True)
    joblib.dump(best_model, "models/best_healthcare_no_show_model.joblib")
    return results

if __name__ == "__main__":
    data_path = sys.argv[1] if len(sys.argv) > 1 else "cleaned_healthcare_appointments.csv"
    if os.path.exists(data_path):
        raw = pd.read_csv(data_path)
        cleaned = load_and_clean_data(raw)
        engineered = feature_engineering(cleaned)
        train_predictive_models(engineered)
    else:
        print(f"Please provide dataset path: python {sys.argv[0]} <path_to_csv>")
