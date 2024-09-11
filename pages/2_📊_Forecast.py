import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import os

# Streamlit app configuration
st.set_page_config(page_title='Stock Market Prediction', page_icon='📊')
st.markdown("<h1 style='text-align: center;'>Stock Market Forecasting using LSTM</h1>", unsafe_allow_html=True)

# Path to store precomputed plots
plot_storage_path = 'D:/Seventh Semester/Capstone Design Project/Stock-Market-Project/plots'

# Cache stock data download
@st.cache_data(ttl=86400)  # Cache data for 1 day (24 hours)
def load_stock_data(ticker):
    data = yf.download(tickers=ticker, start='2023-09-1', end='2024-09-1', interval='1d')
    data.sort_index(inplace=True)
    return data

# Stock selection
ticker = st.selectbox('Stock Name', ['MRF.NS', 'RELIANCE.NS', '^NSEI', 'SBIN.NS', 'AAPL'])

# Check if plot already exists in storage
plot_file_path = os.path.join(plot_storage_path, f'{ticker}_prediction_plot.png')

if os.path.exists(plot_file_path):
    # Load the precomputed plot from storage
    st.image(plot_file_path)
else:
    # If no precomputed plot, compute and save the plot (one-time operation)
    data = load_stock_data(ticker)

    # Data Normalization
    scaler = MinMaxScaler()
    scaler_values = scaler.fit_transform(data[data.columns])
    df_scaled = pd.DataFrame(scaler_values, columns=data.columns, index=data.index)

    # Create sequences function
    def create_sequences(data, window_size):
        X, y = [], []
        for i in range(window_size, len(data)):
            X.append(data.iloc[i-window_size:i].values)
            y.append(data.iloc[i].values)
        return np.array(X), np.array(y)

    window_size = 60
    X, y = create_sequences(df_scaled, window_size)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Load the trained LSTM model and predict (cached)
    model_path = f'D:/Seventh Semester/Capstone Design Project/Stock-Market-Project/models/{ticker}.keras'
    model = load_model(model_path)
    predictions = model.predict(X_test)

    # Inverse Scaling
    predictions = scaler.inverse_transform(predictions)
    y_test_rescaled = scaler.inverse_transform(y_test)

    # Plotting the results
    fig, axs = plt.subplots(2, 3, figsize=(14, 7))  # Create a grid of subplots
    axs = axs.ravel()  # Flatten the axes array for easier indexing

    for i, col in enumerate(df_scaled.columns):
        axs[i].plot(y_test_rescaled[:, i], color='blue', label=f'Actual {col}')
        axs[i].plot(predictions[:, i], color='red', label=f'Predicted {col}')
        axs[i].set_title(f'{col} Prediction')
        axs[i].set_xlabel(f'{col} Price')
        axs[i].legend()

    plt.tight_layout()

    # Save the plot for future use
    fig.savefig(plot_file_path)

    # Display the plot in Streamlit
    st.pyplot(fig)
