# app.py
from flask import Flask, render_template, jsonify
import random
import os
from datetime import datetime

# import Utilities as Ut, Market_Data_Utilities as Mdu, Ineractive_Data_Utilities as Idu

app = Flask(__name__)

# List of available instruments
INSTRUMENTS = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 
    'TSLA', 'NVDA', 'JPM', 'V', 'WMT',
    'JNJ', 'PG', 'MA', 'UNH', 'HD'
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/instruments')
def get_instruments():
    # Randomly select 3 instruments
    selected = random.sample(INSTRUMENTS, 3)
    
    # Simulate LTP data
    instruments_data = []
    for symbol in selected:
        # Random price between 50 and 500
        price = round(random.uniform(50, 500), 2)
        instruments_data.append({
            'symbol': symbol,
            'ltp': price,
            'lastUpdate': datetime.now().strftime('%H:%M:%S')
        })
    
    return jsonify(instruments_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
