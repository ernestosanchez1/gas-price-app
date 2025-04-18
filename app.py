from flask import Flask, request, render_template
import requests
import os  

app = Flask(__name__)

def get_exchange_rate():
    endpoint = "https://openexchangerates.org/api/latest.json"
    api_key = "b82552a45fb44b0db8b7ed355b9d9833"  # Consider using environment variables later
    #api_key = os.environ.get('OPEN_EXCHANGE_RATES_API_KEY') # Get API key from environment variables
    response = requests.get(endpoint, params={"app_id": api_key})
    return response.json()["rates"]["CAD"]

@app.route('/', methods=['GET', 'POST'])
def compare():
    if request.method == 'POST':
        try:
            # Get user inputs
            van_gas_lt = float(request.form['van_price'])
            usa_gas_gal = float(request.form['usa_price'])
            amount_of_lts = float(request.form['liters'])
            
            # Apply discount only if checkbox was checked
            apply_discount = 'apply_discount' in request.form
            if apply_discount:
                van_gas_lt -= 0.08
            
            # Get live exchange rate
            usd_cad_rate = get_exchange_rate()
            
            # Calculations
            van_total = van_gas_lt * amount_of_lts
            usa_total = (amount_of_lts / 3.78541) * usa_gas_gal * usd_cad_rate
            savings = abs(van_total - usa_total)
            cheaper = "USA" if usa_total < van_total else "Canada"
            usa_per_liter = (usa_total / amount_of_lts)
            percent_cheaper = round(((van_total - usa_total) / usa_total) * 100, 1) if usa_total != 0 else 0
            
            # Prepare display price (show original if discount was applied)
            van_price_display = van_gas_lt + 0.08 if apply_discount else van_gas_lt
            
            return render_template('result.html',
                               van_price=van_price_display,
                               usa_price=usa_gas_gal,
                               liters=amount_of_lts,
                               van_total=round(van_total, 2),
                               usa_total=round(usa_total, 2),
                               savings=round(savings, 2),
                               cheaper=cheaper,
                               usa_per_liter=round(usa_per_liter, 2),
                               exchange_rate=round(usd_cad_rate, 4),
                               percent_cheaper=percent_cheaper,
                               discount_applied=apply_discount)  # Pass to template if needed
                               
        except Exception as e:
            error = f"Error: {str(e)}"
            return render_template('index.html', error=error)
    
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)