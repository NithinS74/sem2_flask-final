from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

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

# Initialize database
def init_db():
    conn = sqlite3.connect('car_rental.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            car_name TEXT NOT NULL,
            rental_hours INTEGER NOT NULL,
            total_cost INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

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
        
        # Insert user data into the database
        conn = sqlite3.connect('car_rental.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (name, age, email, phone) VALUES (?, ?, ?, ?)', (name, age, email, phone))
        conn.commit()
        conn.close()

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
        
        # Retrieve the latest user_id
        conn = sqlite3.connect('car_rental.db')
        c = conn.cursor()
        c.execute('SELECT id FROM users ORDER BY id DESC LIMIT 1')
        user_id = c.fetchone()[0]
        conn.close()
        
        return redirect(url_for('process_payment', car_name=car_name, rental_hours=rental_hours, user_id=user_id))
    return render_template('select_car.html', cars=cars)

@app.route('/process_payment/<car_name>/<rental_hours>/<user_id>', methods=['GET', 'POST'])
def process_payment(car_name, rental_hours, user_id):
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        expiry_date = request.form.get('expiry_date')
        cvv = request.form.get('cvv')
        if not all([card_number, expiry_date, cvv]):
            flash("Please fill in all payment details.", "error")
            return redirect(url_for('process_payment', car_name=car_name, rental_hours=rental_hours, user_id=user_id))
        
        # Calculate total cost based on price per hour and rental hours
        price_per_hour = next((car["price_per_hour"] for car in cars if car["model"] in car_name), 0)
        total_cost = price_per_hour * int(rental_hours)
        
        # Insert rental data into the database
        conn = sqlite3.connect('car_rental.db')
        c = conn.cursor()
        c.execute('INSERT INTO rentals (user_id, car_name, rental_hours, total_cost) VALUES (?, ?, ?, ?)', 
                  (user_id, car_name, rental_hours, total_cost))
        conn.commit()
        conn.close()
        
        flash("Payment successful!", "success")
        return redirect(url_for('thank_you'))
    
    return render_template('process_payment.html', car_name=car_name, rental_hours=rental_hours)

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
