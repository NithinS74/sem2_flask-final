from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'secret_key'

# Sample data for cars with predefined prices
cars = [
    {"brand": "Toyota", "model": "Corolla", "price_per_hour": 100},
    {"brand": "Honda", "model": "Civic", "price_per_hour": 250},
    {"brand": "Ford", "model": "Mustang", "price_per_hour": 800},
    {"brand": "Jeep", "model": "Wrangler", "price_per_hour": 500},
    {"brand": "Chevy", "model": "Tahoe", "price_per_hour": 650}
]

@app.route('/', methods=['GET', 'POST'])
def enter_details():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        email = request.form.get('email')
        phone = request.form.get('phone')
        if not all([name, age, email, phone]):
            flash("Please fill in all fields.", "error")
            return redirect(url_for('enter_details'))
        return redirect(url_for('select_car'))
    return render_template('enter_details.html')

@app.route('/select_car', methods=['GET', 'POST'])
def select_car():
    if request.method == 'POST':
        car_name = request.form.get('car_name')
        rental_hours = request.form.get('rental_hours')
        if not all([car_name, rental_hours]):
            flash("Please select a car and specify rental hours.", "error")
            return redirect(url_for('select_car'))
        return redirect(url_for('process_payment', car_name=car_name, rental_hours=rental_hours))
    return render_template('select_car.html', cars=cars)

@app.route('/process_payment/<car_name>/<rental_hours>', methods=['GET', 'POST'])
def process_payment(car_name, rental_hours):
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        expiry_date = request.form.get('expiry_date')
        cvv = request.form.get('cvv')
        if not all([card_number, expiry_date, cvv]):
            flash("Please fill in all payment details.", "error")
            return redirect(url_for('process_payment', car_name=car_name, rental_hours=rental_hours))
        flash("Payment successful!", "success")
        return redirect(url_for('thank_you'))
    
    # Calculate total cost based on price per hour and rental hours
    price_per_hour = next((car["price_per_hour"] for car in cars if car["model"] in car_name), 0)
    total_cost = price_per_hour * int(rental_hours)
    
    return render_template('process_payment.html', car_name=car_name, rental_hours=rental_hours,
                           price_per_hour=price_per_hour, total_cost=total_cost)

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)
