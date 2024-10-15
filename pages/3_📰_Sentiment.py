import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Alpha Vantage API endpoint and key
api_key = "ZA9N9AMMAT2QFUDU"
endpoint = "https://www.alphavantage.co/query"
function = "NEWS_SENTIMENT"

# Get stock data for the last 30 days using Yahoo Finance
def fetch_stock_data(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data

# Fetch news sentiment data from Alpha Vantage
def fetch_news_sentiment(ticker):
    params = {
        "function": function,
        "tickers": ticker,
        "apikey": api_key,
        "limit": 50
    }
    response = requests.get(endpoint, params=params)
    return response.json()

# Categorize sentiment into Good, Bad, or Neutral
def categorize_sentiment(score):
    if score > 0.15:
        return "Good"
    elif score < -0.15:
        return "Bad"
    else:
        return "Neutral"

# Generate buy/sell recommendation based on sentiment
def generate_recommendation(sentiment_counts):
    if sentiment_counts.get("Good", 0) > sentiment_counts.get("Bad", 0):
        recommendation = "BUY"
    elif sentiment_counts.get("Bad", 0) > sentiment_counts.get("Good", 0):
        recommendation = "SELL"
    else:
        recommendation = "HOLD"
    return recommendation

# Main function to create the Streamlit app
def main():
    st.set_page_config(page_title='Stock Market Prediction', page_icon='📰')
    st.markdown("<h1 style='text-align: center;'>Sentiment Analysis</h1>", unsafe_allow_html=True)

    # Input field for the ticker
    ticker = st.text_input("Enter Ticker Symbol:", "AAPL")

    if st.button("Get Recommendation"):
        if ticker:
            # Fetch stock data
            stock_data = fetch_stock_data(ticker)

            # Fetch news sentiment data
            news_data = fetch_news_sentiment(ticker)

            if 'feed' in news_data:
                # Extract sentiment scores and categorize them
                sentiment_scores = [item['overall_sentiment_score'] for item in news_data['feed']]
                sentiments = [categorize_sentiment(score) for score in sentiment_scores]

                # Generate recommendation based on sentiment analysis
                sentiment_counts = pd.Series(sentiments).value_counts()
                recommendation = generate_recommendation(sentiment_counts)

                # Display recommendation in a card format
                st.subheader("Recommendation:")
                st.write(f"**According to the Sentiment Analysis for {ticker}, you can {recommendation} it**")

                # Optionally, you can display sentiment distribution
                sentiment_counts.plot(kind='bar', color=['green', 'red', 'gray'])
                plt.title('Sentiment Analysis of News Articles')
                plt.xlabel('Sentiment Category')
                plt.ylabel('Number of Articles')
                st.pyplot(plt)
            else:
                st.error("No news sentiment data found for the entered ticker.")

        else:
            st.error("Please enter a valid ticker symbol.")

if __name__ == "__main__":
    main()
