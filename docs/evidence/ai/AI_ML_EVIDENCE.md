# SmartPark AI — AI and Machine Learning Evidence

## 1. AI Objective

The machine-learning component of SmartPark AI predicts future parking occupancy.

The prediction is then used by other system components including:

- parking-demand analysis;
- parking recommendations;
- AI-assisted dynamic pricing;
- administrator analytics.

---

## 2. Prediction Model

The final production model uses XGBoost regression.

Input features:

1. hour;
2. day of week;
3. previous occupancy;
4. current occupancy;
5. traffic level;
6. weather;
7. event level;
8. parking price;
9. total parking spaces.

The target variable is predicted parking occupancy.

---

## 3. Model Comparison

Several regression models were evaluated before selecting the final model.

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| XGBoost | 4.7752 | 6.1025 | 0.9139 |
| Gradient Boosting | 4.8638 | 6.2022 | 0.9111 |
| Linear Regression | 5.4902 | 6.8915 | 0.8902 |
| Random Forest | 5.6822 | 7.1616 | 0.8814 |

XGBoost achieved the strongest overall performance and was selected for further tuning.

---

## 4. Hyperparameter Tuning

The tuned XGBoost model uses:

- learning_rate: 0.08
- max_depth: 2
- min_child_weight: 7
- n_estimators: 650
- subsample: 0.70
- colsample_bytree: 0.90
- reg_alpha: 0.01
- reg_lambda: 3

Best cross-validation RMSE:

6.0172

---

## 5. Final Evaluation

The tuned model was evaluated using a separate unseen synthetic dataset generated using a different random seed.

Final results:

| Metric | Result |
|---|---:|
| MAE | 4.7191 |
| RMSE | 5.9884 |
| R² | 0.9159 |
| Median Absolute Error | 3.8522 |
| 90th Percentile Absolute Error | 9.8915 |

These results must be described as:

**unseen synthetic evaluation under the same simulation assumptions**

They should not be described as real-world validation.

---

## 6. Feature Importance

Approximate feature importance from the tuned XGBoost model:

| Feature | Importance |
|---|---:|
| Current Occupancy | 46.41% |
| Traffic Level | 17.73% |
| Event Level | 12.37% |
| Previous Occupancy | 7.82% |
| Parking Price | 4.86% |
| Hour | 4.12% |
| Weather | 3.96% |
| Day of Week | 1.87% |
| Parking Capacity | 0.86% |

Current occupancy was the most influential feature in the prototype model.

---

## 7. Prediction Workflow

The implemented workflow is:

Synthetic Dataset
→ Data Preparation
→ Feature Selection
→ Model Training
→ Model Comparison
→ Hyperparameter Tuning
→ Evaluation
→ Model Persistence
→ FastAPI Prediction Service
→ Vue Frontend

The trained model is stored using Joblib and loaded by the backend prediction service.

---

## 8. Parking Recommendations

Prediction and recommendation are separate components.

The XGBoost model predicts parking occupancy.

The recommendation service ranks parking locations using information including:

- distance;
- parking price;
- current availability;
- current occupancy;
- predicted occupancy;
- parking rating.

Recommendation modes include:

- balanced;
- closest;
- cheapest;
- most available;
- low demand.

---

## 9. AI-Assisted Dynamic Pricing

Dynamic pricing uses AI-predicted occupancy as one pricing input.

The pricing calculation considers:

- base hourly rate;
- reservation time;
- current occupancy;
- predicted occupancy.

The pricing multiplier is bounded between:

0.75× and 1.50×

The pricing policy itself is a project-designed heuristic.

It is not a machine-learning pricing model.

The XGBoost model contributes predicted demand to the pricing calculation.

---

## 10. Dynamic Pricing Reproducibility

At booking time, the system stores:

- base hourly rate;
- applied hourly rate;
- pricing multiplier;
- current occupancy;
- predicted occupancy;
- model version.

This creates a reproducible pricing snapshot and preserves the accepted booking rate.

---

## 11. Prototype Limitations

The current ML evaluation uses synthetic data.

The reservation service does not currently use live external traffic, weather or event feeds.

Baseline values are used for unavailable external context when dynamic pricing requests predictions.

Future validation should use:

- real parking occupancy data;
- traffic APIs;
- weather APIs;
- event feeds;
- parking sensor data;
- larger real-world datasets.

---

## 12. Interpretation

The results demonstrate that XGBoost can model the relationships present in the prototype synthetic parking dataset with strong predictive performance.

However, these results demonstrate technical feasibility under the simulation assumptions rather than proven performance in a deployed real-world parking environment.

