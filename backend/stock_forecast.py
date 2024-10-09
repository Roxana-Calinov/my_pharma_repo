"""
Necessary libraries:
Pandas -> for data manipulation
NumPy -> for numeric operations
Scikit-learn -> for machine learning algorithms and model validation
XGBoost -> XGBoost algorithm implementation
SQLAlchemy -> interacting with the DB
datetime -> working with the date & time
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from sqlalchemy.orm import Session
from models import MedicationDB
from datetime import datetime


def prepare_data(df, medication_id):
    """
    Prepare and aggregate data for a specific medication.
    """
    df_med = df[df['id'] == medication_id].copy()
    df_med['order_date'] = pd.to_datetime(df_med['order_date'])
    df_med = df_med.sort_values('order_date')

    #Aggregate daily data
    df_agg = df_med.groupby('order_date').agg({
        'quantity': 'sum',
        'quantity_ordered': 'sum',
        'price': 'mean',
        'stock': 'first'
    }).reset_index()

    #Add derived features
    df_agg['day_of_week'] = df_agg['order_date'].dt.dayofweek
    df_agg['month'] = df_agg['order_date'].dt.month
    df_agg['year'] = df_agg['order_date'].dt.year
    df_agg['demand_ma_7'] = df_agg['quantity_ordered'].rolling(window=7, min_periods=1).mean()
    df_agg['demand_ma_30'] = df_agg['quantity_ordered'].rolling(window=30, min_periods=1).mean()
    df_agg['season'] = (df_agg['month'] % 12 + 3) // 3
    df_agg['trend'] = np.arange(len(df_agg))

    return df_agg


def get_yearly_comparison(df, current_date):
    """
    Calculate total quantity for current month from the past 3 years (from dataset)
    """
    current_month = current_date.month
    one_year_ago = df[(df['month'] == current_month) & (df['year'] == current_date.year - 1)]['quantity_ordered'].sum()
    two_years_ago = df[(df['month'] == current_month) & (df['year'] == current_date.year - 2)]['quantity_ordered'].sum()
    three_years_ago = df[(df['month'] == current_month) & (df['year'] == current_date.year - 3)][
        'quantity_ordered'].sum()
    return one_year_ago, two_years_ago, three_years_ago


def split_data(X, y):
    """
    Split the data into train, validation, and test sets.
    """
    #First split: separate the test set (20% of data)
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    #Second split: separate train and validation from the remaining 80%
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25,
                                                      shuffle=False)   #0.25 x 0.8 = 0.2 of original data

    return X_train, X_val, X_test, y_train, y_val, y_test


def train_models(X_train, y_train, X_val, y_val):
    """
    Train Random Forest and XGBoost models with validation.
    """
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=8, min_samples_leaf=5, random_state=42)
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.03, max_depth=5, random_state=42)

    #Random Forest
    rf_model.fit(X_train, y_train)
    #XGBoost
    xgb_model.fit(X_train, y_train)

    return rf_model, xgb_model


def predict_optimal_stock(db: Session, medication_name: str, csv_path: str):
    """
    Predict optimal stock for a specific medication
    """
    #Fetch medication from DB
    medications = db.query(MedicationDB).filter(MedicationDB.name == medication_name).all()

    if not medications:
        return {"error": f"{medication_name} not found in database."}

    current_central_stock = medications[0].stock
    current_pharmacy_stock = sum(med.quantity for med in medications)
    total_current_stock = current_central_stock + current_pharmacy_stock
    medication_id = medications[0].id

    #Prepare historical data from dataset
    historical_data = pd.read_csv(csv_path)
    df_agg = prepare_data(historical_data, medication_id)

    if df_agg.empty:
        return {"error": f"No historical data found for {medication_name} medication."}

    #Define features and target
    features = ['stock', 'quantity', 'price', 'day_of_week', 'month', 'year',
                'demand_ma_7', 'demand_ma_30', 'season', 'trend']
    target = 'quantity_ordered'

    X = df_agg[features]
    y = df_agg[target]

    #Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    #Split data
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(X_scaled, y)

    #Combine train and validation sets for final training
    X_train_full = np.vstack((X_train, X_val))
    y_train_full = np.concatenate((y_train, y_val))

    #Train models
    rf_model, xgb_model = train_models(X_train_full, y_train_full, None, None)

    #Evaluate models on test set
    rf_pred_test = rf_model.predict(X_test)
    xgb_pred_test = xgb_model.predict(X_test)
    rf_mse = mean_squared_error(y_test, rf_pred_test)
    xgb_mse = mean_squared_error(y_test, xgb_pred_test)
    rf_r2 = r2_score(y_test, rf_pred_test)
    xgb_r2 = r2_score(y_test, xgb_pred_test)

    #Prepare data for the next month prediction
    current_date = datetime.now()
    next_month_dates = pd.date_range(start=current_date, periods=30, freq='D')
    next_month_data = pd.DataFrame({
        'stock': [current_central_stock] * 30,
        'quantity': [current_pharmacy_stock] * 30,
        'price': [df_agg['price'].mean()] * 30,
        'day_of_week': next_month_dates.dayofweek,
        'month': next_month_dates.month,
        'year': next_month_dates.year,
        'demand_ma_7': [df_agg['demand_ma_7'].iloc[-1]] * 30,
        'demand_ma_30': [df_agg['demand_ma_30'].iloc[-1]] * 30,
        'season': [(month % 12 + 3) // 3 for month in next_month_dates.month],
        'trend': range(len(df_agg), len(df_agg) + 30)
    })

    #Make forecast for next month
    next_month_data_scaled = scaler.transform(next_month_data[features])
    rf_pred = rf_model.predict(next_month_data_scaled)
    xgb_pred = xgb_model.predict(next_month_data_scaled)
    ensemble_pred = (rf_pred + xgb_pred) / 2

    predicted_monthly_demand = ensemble_pred.sum()

    #Get historical comparison
    one_year_ago, two_years_ago, three_years_ago = get_yearly_comparison(df_agg, current_date)

    #Calculate weighted prediction
    weighted_prediction = (
        predicted_monthly_demand * 0.4 +
        one_year_ago * 0.3 +
        two_years_ago * 0.2 +
        three_years_ago * 0.1
    )

    #Calculate safety stock
    recent_demands = [one_year_ago, two_years_ago, three_years_ago]
    safety_stock = np.std(recent_demands) * 1.96

    #Calculate optimal order quantity
    optimal_order_quantity = max(0, weighted_prediction + safety_stock - total_current_stock)

    #Limit the order quantity
    max_order = max(weighted_prediction, np.mean(recent_demands)) * 1.5
    optimal_order_quantity = min(optimal_order_quantity, max_order)

    #Return results
    return {
        "medication_name": medication_name,
        "current_central_stock": current_central_stock,
        "current_pharmacy_stock": current_pharmacy_stock,
        "total_current_stock": total_current_stock,
        "predicted_monthly_demand": int(weighted_prediction),
        "recommended_order_quantity": int(optimal_order_quantity),
        "safety_stock": int(safety_stock),
        "historical_comparison": {
            "one_year_ago": int(one_year_ago),
            "two_years_ago": int(two_years_ago),
            "three_years_ago": int(three_years_ago)
        },
        "model_performance": {
            "random_forest_mse": rf_mse,
            "random_forest_r2": rf_r2,
            "xgboost_mse": xgb_mse,
            "xgboost_r2": xgb_r2
        }
    }
