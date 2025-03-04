from flask import Flask, render_template, jsonify
import random
from datetime import datetime
import os

import Utilities as Ut, Market_Data_Utilities as Mdu, Ineractive_Data_Utilities as Idu

app = Flask(__name__)

# List of available instruments
INSTRUMENTS = [
    2475, 5900, 7229, 15083, 1394
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/instruments')
def get_instruments():
    # Randomly select 3 instruments
    selected = random.sample(INSTRUMENTS, 3)
    
    # Generate data
    data = [{
        'symbol': symbol,
        'ltp': Mdu.Fetch_Ltp(Bt, 1, symbol),
        'lastUpdate': datetime.now().strftime('%H:%M:%S')
    } for symbol in selected]
    
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
