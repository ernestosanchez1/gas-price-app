from flask import Flask, request, render_template
import requests
import os  # Import the os module

app = Flask(__name__)

def get_exchange_rate():
    endpoint = "https://openexchangerates.org/api/latest.json"
    api_key = os.environ.get('OPEN_EXCHANGE_RATES_API_KEY') # Get API key from environment variables
    response = requests.get(endpoint, params={"app_id": api_key})
    return response.json()["rates"]["CAD"]

@app.route('/', methods=['GET', 'POST'])
def compare():
    if request.method == 'POST':
        try:
            # Get user inputs
            van_gas_lt = float(request.form['van_price']) - 0.08  # Apply Mobil discount
            usa_gas_gal = float(request.form['usa_price'])
            amount_of_lts = float(request.form['liters'])
            
            # Get live exchange rate
            usd_cad_rate = get_exchange_rate()
            
            # Calculations
            van_total = van_gas_lt * amount_of_lts
            usa_total = (amount_of_lts / 3.78541) * usa_gas_gal * usd_cad_rate
            savings = abs(van_total - usa_total)
            cheaper = "USA" if usa_total < van_total else "Canada"
            usa_per_liter = (usa_total / amount_of_lts)
            percent_cheaper = round(((van_total - usa_total) / usa_total) * 100, 1) if usa_total != 0 else 0
            
            return render_template('result.html',
                               van_price=van_gas_lt + 0.08,  # Show original price to user
                               usa_price=usa_gas_gal,
                               liters=amount_of_lts,
                               van_total=round(van_total, 2),
                               usa_total=round(usa_total, 2),
                               savings=round(savings, 2),
                               cheaper=cheaper,
                               usa_per_liter=round(usa_per_liter, 2),
                               exchange_rate=round(usd_cad_rate, 4),
                               percent_cheaper=percent_cheaper)
                               
        except Exception as e:
            error = f"Error: {str(e)}"
            return render_template('index.html', error=error)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)