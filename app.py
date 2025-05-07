from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    if not os.path.exists('users.db'):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER,
                image TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                checkin TEXT NOT NULL,
                checkout TEXT NOT NULL,
                comment TEXT,
                processed INTEGER DEFAULT 0,
                cancelled INTEGER DEFAULT 0,
                FOREIGN KEY(room_id) REFERENCES rooms(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed INTEGER DEFAULT 0
            )
        ''')
        rooms = [
            ('Одноместный стандарт', 'Уютный номер с одной кроватью и всеми необходимыми удобствами для комфортного отдыха. Завтрак, обед и ужин включены в стоимость. Уборка один раз в день.', 2000, 'room1.jpg'),
            ('Двуместный стандарт', 'Просторный номер с двумя кроватями и панорамными окнами с выходом на балкон. Идеален для пар или друзей. Завтрак, обед и ужин включены в стоимость. Уборка один раз в день.', 4000, 'room2.jpg'),
            ('Одноместный люкс', 'Роскошный люкс с большой кроватью, панорамными окнами и дополнительными удобствами для особого комфорта. Премиум завтрак, обед и ужин включены в стоимость. Открыт бар с бесплатным посещением. Уборка несколько раз в день.', 9000, 'room3.jpg'),
            ('Двуместный люкс', 'Премиум люкс с двумя кроватями, отдельной зоной отдыха и великолепным видом из окна. Идеален для романтического отдыха или деловых поездок. Премиум завтрак, обед и ужин включены в стоимость. Открыт бар с бесплатным посещением. Уборка несколько раз в день.', 11000, 'room4.jpg')
        ]
        cursor.executemany('INSERT INTO rooms (name, description, price, image) VALUES (?, ?, ?, ?)', rooms)
        conn.commit()
        conn.close()

init_db()

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/rooms')
def rooms():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, price, image FROM rooms')
    rooms = [
        {'id': row[0], 'name': row[1], 'description': row[2], 'price': row[3], 'image': row[4]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return render_template('rooms.html', rooms=rooms)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    room_id = request.args.get('room_id', type=int)
    room_name = None
    error = None
    message = None

    if room_id:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM rooms WHERE id=?', (room_id,))
        row = cursor.fetchone()
        if row:
            room_name = row[0]
        conn.close()

    if request.method == 'POST':
        if not request.form.get('room_id'):
            error = "Не выбран номер для бронирования. Пожалуйста, выберите номер на странице 'Номера'."
            return render_template('booking.html', room_id=None, room_name=None, error=error, message=None)

        room_id = int(request.form['room_id'])
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM rooms WHERE id=?', (room_id,))
        row = cursor.fetchone()
        room_name = row[0] if row else None
        conn.close()

        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        comment = request.form.get('comment', '')

        try:
            checkin_date = datetime.strptime(checkin, "%Y-%m-%d")
            checkout_date = datetime.strptime(checkout, "%Y-%m-%d")
            if checkin_date >= checkout_date:
                error = "Дата выезда должна быть позже даты заезда."
        except Exception:
            error = "Некорректный формат дат."

        if not error:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM bookings 
                WHERE room_id = ? AND cancelled = 0
                AND (
                    (checkin < ? AND checkout > ?) OR
                    (checkin < ? AND checkout > ?) OR
                    (checkin >= ? AND checkout <= ?)
                )
            ''', (room_id, checkout, checkin, checkout, checkin, checkin, checkout))
            if cursor.fetchone():
                error = "Этот номер уже забронирован на выбранные даты!"
            else:
                cursor.execute('''
                    INSERT INTO bookings (room_id, name, phone, email, checkin, checkout, comment)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (room_id, name, phone, email, checkin, checkout, comment))
                conn.commit()
                message = "Ваша заявка отправлена! Мы свяжемся с вами."
            conn.close()

    return render_template('booking.html', room_id=room_id, room_name=room_name, error=error, message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Пользователь с таким именем или email уже существует!"
            return render_template('register.html', error=error)
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect(url_for('cabinet'))
        else:
            error = "Неверный логин или пароль"
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/cabinet')
def cabinet():
    if 'user' in session:
        return render_template('cabinet.html', username=session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# ----------- ОТЗЫВЫ -----------

@app.route('/review', methods=['POST'])
def review():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reviews (name, email, message) VALUES (?, ?, ?)', (name, email, message))
    conn.commit()
    conn.close()
    return render_template('review_thankyou.html', name=name)

@app.route('/admin/reviews')
def admin_reviews():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, message, created_at, processed FROM reviews ORDER BY created_at DESC')
    reviews = cursor.fetchall()
    conn.close()
    return render_template('admin_reviews.html', reviews=reviews)

@app.route('/admin/process_review/<int:review_id>', methods=['POST'])
def process_review(review_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE reviews SET processed=1 WHERE id=?', (review_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_reviews'))

@app.route('/admin/unprocess_review/<int:review_id>', methods=['POST'])
def unprocess_review(review_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE reviews SET processed=0 WHERE id=?', (review_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_reviews'))

@app.route('/admin/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reviews WHERE id=?', (review_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_reviews'))

# ----------- БРОНИРОВАНИЯ -----------

@app.route('/admin/bookings')
def admin_bookings():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, r.name, b.name, b.phone, b.email, b.checkin, b.checkout, b.comment, b.processed, b.cancelled
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        ORDER BY b.id DESC
    ''')
    bookings = cursor.fetchall()
    conn.close()
    return render_template('admin_bookings.html', bookings=bookings)

@app.route('/admin/mark_processed/<int:booking_id>', methods=['POST'])
def mark_processed(booking_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE bookings SET processed=1 WHERE id=?', (booking_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_bookings'))

@app.route('/admin/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE bookings SET cancelled=1 WHERE id=?', (booking_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_bookings'))

if __name__ == '__main__':
    app.run(debug=True)