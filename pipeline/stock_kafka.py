import yfinance as yf
from confluent_kafka import Producer
import json
import time

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()}")
        
producer = Producer({'bootstrap.servers': 'localhost:9092'})

def fetch_and_send_stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1y", interval="1d")
    if not data.empty:
        for index, row in data.iterrows():
            stock_info = {
                'symbol': symbol,
                'date': str(index),  
                'open': float(row['Open']),
                'close': float(row['Close']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'volume': int(row['Volume'])
            }

            producer.produce(
                'stock-data',
                key=symbol.encode('utf-8'),
                value=json.dumps(stock_info).encode('utf-8'),
                callback=delivery_report
            )
            producer.poll(0)  
            print(f"Sent data for {index}")  
            
            time.sleep(1)  
    else:
        print(f"No data available for {symbol} at this time.")

if __name__ == '__main__':
    fetch_and_send_stock_data('AAPL')  
    producer.flush()  
