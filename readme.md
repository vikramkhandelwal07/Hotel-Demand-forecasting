# 🏨 ProHotelytics: Hotel Demand Forecasting & Analytics

🔗 **Live Apps**  
- 🔮 [Forecasting App](https://prohotelytics.streamlit.app/)  
- 📊 [Analytics Dashboard](https://prohotelyticsdashboard.streamlit.app/)

---

## 📌 Overview

ProHotelytics is a data-driven solution for analyzing and forecasting hotel booking demand. It includes two interactive Streamlit apps powered by traditional and deep learning models for accurate forecasting and insightful data exploration.

---

## 🚀 Features

- In-depth EDA to identify trends, seasonality, and anomalies.
- Time series forecasting with ARIMA, SARIMAX, Prophet, RNN, and LSTM.
- Interactive dashboards for hotel booking analytics.
- User-friendly web apps for business decision-making.

---

## 🧰 Tech Stack

- Python, Pandas, NumPy, Scikit-learn
- Statsmodels, Prophet, TensorFlow/Keras
- Plotly, Matplotlib, Seaborn
- Streamlit

---

## 🗂️ Run Locally

```bash
git clone https://github.com/yourusername/hotel-demand-forecasting.git
cd hotel-demand-forecasting
pip install -r requirements.txt

# Run apps
cd streamlit_apps/forecasting_app
streamlit run app.py

cd ../analytics_app
streamlit run app.py
