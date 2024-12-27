from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

def init_db():
    # Delete existing database if it exists
    if os.path.exists('mawater.db'):
        os.remove('mawater.db')
    
    conn = sqlite3.connect('mawater.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  firstName TEXT NOT NULL,
                  lastName TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  phone TEXT,
                  is_admin INTEGER DEFAULT 0)''')
    
    # Create cars table with approval status
    c.execute('''CREATE TABLE IF NOT EXISTS cars
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  make TEXT NOT NULL,
                  model TEXT NOT NULL,
                  year INTEGER NOT NULL,
                  price REAL NOT NULL,
                  mileage INTEGER,
                  condition TEXT,
                  description TEXT,
                  user_id INTEGER,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Create favorites table
    c.execute('''CREATE TABLE IF NOT EXISTS favorites
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  car_id INTEGER NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id),
                  FOREIGN KEY (car_id) REFERENCES cars (id),
                  UNIQUE(user_id, car_id))''')
    
    # Create messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender_id INTEGER NOT NULL,
                  receiver_id INTEGER NOT NULL,
                  car_id INTEGER,
                  message TEXT NOT NULL,
                  read INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (sender_id) REFERENCES users (id),
                  FOREIGN KEY (receiver_id) REFERENCES users (id),
                  FOREIGN KEY (car_id) REFERENCES cars (id))''')
    
    # Create default admin user and test user
    c.execute("INSERT INTO users (firstName, lastName, email, password, is_admin) VALUES (?, ?, ?, ?, ?)",
             ('Admin', 'User', 'admin@mawater974.com', 'admin', 1))
    
    c.execute("INSERT INTO users (firstName, lastName, email, password, is_admin) VALUES (?, ?, ?, ?, ?)",
             ('Duda', 'User', 'dudaduda336@gmail.com', 'duda123', 0))
    
    conn.commit()
    conn.close()
    print("Database initialized with admin user and test user")

# Initialize database
init_db()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    conn = sqlite3.connect('mawater.db')
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        
        if user:
            return jsonify({
                'id': user[0],
                'firstName': user[1],
                'lastName': user[2],
                'email': user[3],
                'phone': user[5],
                'is_admin': bool(user[6])
            })
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone', '')  # Make phone optional
    
    if not all([firstName, lastName, email, password]):
        return jsonify({'error': 'All fields are required'}), 400
    
    conn = sqlite3.connect('mawater.db')
    c = conn.cursor()
    
    try:
        # Check if email already exists
        c.execute("SELECT id FROM users WHERE email = ?", (email,))
        if c.fetchone():
            return jsonify({'error': 'Email already exists'}), 400
            
        # Insert new user
        c.execute("""
            INSERT INTO users (firstName, lastName, email, password, phone, is_admin) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (firstName, lastName, email, password, phone, 0))
        
        conn.commit()
        
        # Get the created user
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        
        return jsonify({
            'id': user[0],
            'firstName': user[1],
            'lastName': user[2],
            'email': user[3],
            'phone': user[5],
            'is_admin': bool(user[6])
        })
        
    except Exception as e:
        print(f"Error during registration: {str(e)}")
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/cars', methods=['GET', 'POST'])
def cars():
    if request.method == 'GET':
        # Get query parameters
        make = request.args.get('make')
        model = request.args.get('model')
        year_min = request.args.get('year_min')
        year_max = request.args.get('year_max')
        price_min = request.args.get('price_min')
        price_max = request.args.get('price_max')
        mileage_min = request.args.get('mileage_min')
        mileage_max = request.args.get('mileage_max')
        condition = request.args.get('condition')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'DESC')
        
        conn = sqlite3.connect('mawater.db')
        c = conn.cursor()
        
        try:
            query = "SELECT * FROM cars WHERE status = 'approved'"
            params = []
            
            if make:
                query += " AND make LIKE ?"
                params.append(f"%{make}%")
            if model:
                query += " AND model LIKE ?"
                params.append(f"%{model}%")
            if year_min:
                query += " AND year >= ?"
                params.append(year_min)
            if year_max:
                query += " AND year <= ?"
                params.append(year_max)
            if price_min:
                query += " AND price >= ?"
                params.append(price_min)
            if price_max:
                query += " AND price <= ?"
                params.append(price_max)
            if mileage_min:
                query += " AND mileage >= ?"
                params.append(mileage_min)
            if mileage_max:
                query += " AND mileage <= ?"
                params.append(mileage_max)
            if condition:
                query += " AND condition = ?"
                params.append(condition)
            
            query += f" ORDER BY {sort_by} {sort_order}"
            
            c.execute(query, params)
            cars = c.fetchall()
            
            return jsonify([{
                'id': car[0],
                'make': car[1],
                'model': car[2],
                'year': car[3],
                'price': car[4],
                'mileage': car[5],
                'condition': car[6],
                'description': car[7],
                'user_id': car[8],
                'status': car[9],
                'created_at': car[10]
            } for car in cars])
            
        except Exception as e:
            print(f"Error fetching cars: {str(e)}")
            return jsonify({'error': str(e)}), 400
        finally:
            conn.close()
            
    elif request.method == 'POST':
        try:
            data = request.json
            user_id = data.get('user_id')
            
            if not user_id:
                return jsonify({'error': 'User ID is required'}), 400
            
            # Convert data types
            try:
                year = int(data.get('year', 0))
                price = float(data.get('price', 0))
                mileage = int(data.get('mileage', 0)) if data.get('mileage') else None
            except (ValueError, TypeError) as e:
                return jsonify({'error': 'Invalid data types. Year and price must be numbers.'}), 400
            
            # Validate required fields
            if not all([data.get('make'), data.get('model'), year > 0, price > 0]):
                return jsonify({'error': 'Make, model, year, and price are required'}), 400
            
            conn = sqlite3.connect('mawater.db')
            c = conn.cursor()
            
            try:
                c.execute("""
                    INSERT INTO cars (
                        make, 
                        model, 
                        year, 
                        price, 
                        mileage, 
                        condition, 
                        description, 
                        user_id,
                        status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('make'),
                    data.get('model'),
                    year,
                    price,
                    mileage,
                    data.get('condition'),
                    data.get('description'),
                    user_id,
                    'pending'  # Set initial status as pending
                ))
                
                conn.commit()
                car_id = c.lastrowid
                
                # Fetch the created car
                c.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
                car = c.fetchone()
                
                return jsonify({
                    'message': 'Car listed successfully',
                    'car': {
                        'id': car[0],
                        'make': car[1],
                        'model': car[2],
                        'year': car[3],
                        'price': car[4],
                        'mileage': car[5],
                        'condition': car[6],
                        'description': car[7],
                        'user_id': car[8],
                        'status': car[9],
                        'created_at': car[10]
                    }
                })
                
            except Exception as e:
                print(f"Database error: {str(e)}")
                conn.rollback()
                return jsonify({'error': f'Error saving car: {str(e)}'}), 400
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error listing car: {str(e)}")
            return jsonify({'error': str(e)}), 400

@app.route('/api/cars/<int:car_id>', methods=['GET', 'PUT', 'DELETE'])
def car(car_id):
    conn = sqlite3.connect('mawater.db')
    c = conn.cursor()
    
    if request.method == 'GET':
        try:
            c.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
            car = c.fetchone()
            
            if car:
                return jsonify({
                    'id': car[0],
                    'make': car[1],
                    'model': car[2],
                    'year': car[3],
                    'price': car[4],
                    'mileage': car[5],
                    'condition': car[6],
                    'description': car[7],
                    'user_id': car[8],
                    'status': car[9],
                    'created_at': car[10]
                })
            else:
                return jsonify({'error': 'Car not found'}), 404
                
        except Exception as e:
            print(f"Error fetching car: {str(e)}")
            return jsonify({'error': str(e)}), 400
        finally:
            conn.close()
            
    elif request.method == 'PUT':
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        try:
            # Check if user owns the car or is admin
            c.execute("SELECT user_id FROM cars WHERE id = ?", (car_id,))
            car = c.fetchone()
            
            if not car:
                return jsonify({'error': 'Car not found'}), 404
            
            c.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
            user = c.fetchone()
            
            if car[0] != user_id and not user[0]:
                return jsonify({'error': 'Unauthorized'}), 403
            
            # Update car
            update_fields = []
            params = []
            
            for field in ['make', 'model', 'year', 'price', 'mileage', 'condition', 'description', 'status']:
                if field in data:
                    update_fields.append(f"{field} = ?")
                    params.append(data[field])
            
            if update_fields:
                params.append(car_id)
                query = f"UPDATE cars SET {', '.join(update_fields)} WHERE id = ?"
                c.execute(query, params)
                conn.commit()
                
            return jsonify({'message': 'Car updated successfully'})
            
        except Exception as e:
            print(f"Error updating car: {str(e)}")
            return jsonify({'error': str(e)}), 400
        finally:
            conn.close()
            
    elif request.method == 'DELETE':
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        try:
            # Check if user owns the car or is admin
            c.execute("SELECT user_id FROM cars WHERE id = ?", (car_id,))
            car = c.fetchone()
            
            if not car:
                return jsonify({'error': 'Car not found'}), 404
            
            c.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
            user = c.fetchone()
            
            if car[0] != int(user_id) and not user[0]:
                return jsonify({'error': 'Unauthorized'}), 403
            
            # Delete car
            c.execute("DELETE FROM cars WHERE id = ?", (car_id,))
            conn.commit()
            
            return jsonify({'message': 'Car deleted successfully'})
            
        except Exception as e:
            print(f"Error deleting car: {str(e)}")
            return jsonify({'error': str(e)}), 400
        finally:
            conn.close()

@app.route('/api/messages', methods=['GET', 'POST'])
def messages():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    conn = sqlite3.connect('mawater.db')
    c = conn.cursor()
    
    if request.method == 'GET':
        try:
            # Get all conversations for the user
            c.execute("""
                SELECT DISTINCT 
                    CASE 
                        WHEN m.sender_id = ? THEN m.receiver_id 
                        ELSE m.sender_id 
                    END as other_user_id,
                    u.firstName,
                    u.lastName,
                    c.make,
                    c.model,
                    c.year,
                    MAX(m.created_at) as last_message_time,
                    COUNT(CASE WHEN m.read = 0 AND m.receiver_id = ? THEN 1 END) as unread_count
                FROM messages m
                JOIN users u ON u.id = CASE 
                    WHEN m.sender_id = ? THEN m.receiver_id 
                    ELSE m.sender_id 
                END
                LEFT JOIN cars c ON c.id = m.car_id
                WHERE m.sender_id = ? OR m.receiver_id = ?
                GROUP BY other_user_id
                ORDER BY last_message_time DESC
            """, (user_id, user_id, user_id, user_id, user_id))
            
            conversations = [{
                'other_user_id': row[0],
                'firstName': row[1],
                'lastName': row[2],
                'car_make': row[3],
                'car_model': row[4],
                'car_year': row[5],
                'last_message_time': row[6],
                'unread_count': row[7]
            } for row in c.fetchall()]
            
            return jsonify(conversations)
            
        except Exception as e:
            print(f"Error fetching messages: {str(e)}")
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'POST':
        data = request.json
        receiver_id = data.get('receiver_id')
        car_id = data.get('car_id')
        message = data.get('message')
        
        if not all([receiver_id, message]):
            return jsonify({'error': 'Receiver ID and message are required'}), 400
        
        try:
            c.execute("""
                INSERT INTO messages (sender_id, receiver_id, car_id, message)
                VALUES (?, ?, ?, ?)
            """, (user_id, receiver_id, car_id, message))
            
            conn.commit()
            return jsonify({'message': 'Message sent successfully'})
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return jsonify({'error': str(e)}), 400
        conn.close()

@app.route('/api/messages/<int:conversation_id>', methods=['GET'])
def conversation_messages(conversation_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    conn = sqlite3.connect('mawater.db')
    c = conn.cursor()
    
    try:
        # Mark messages as read
        c.execute("""
            UPDATE messages 
            SET read = 1 
            WHERE receiver_id = ? AND sender_id = ?
        """, (user_id, conversation_id))
        
        # Get conversation messages
        c.execute("""
            SELECT 
                m.*,
                s.firstName as sender_firstName,
                s.lastName as sender_lastName,
                r.firstName as receiver_firstName,
                r.lastName as receiver_lastName
            FROM messages m
            JOIN users s ON s.id = m.sender_id
            JOIN users r ON r.id = m.receiver_id
            WHERE (m.sender_id = ? AND m.receiver_id = ?)
               OR (m.sender_id = ? AND m.receiver_id = ?)
            ORDER BY m.created_at ASC
        """, (user_id, conversation_id, conversation_id, user_id))
        
        messages = [{
            'id': row[0],
            'sender_id': row[1],
            'receiver_id': row[2],
            'car_id': row[3],
            'message': row[4],
            'read': row[5],
            'created_at': row[6],
            'sender_name': f"{row[7]} {row[8]}",
            'receiver_name': f"{row[9]} {row[10]}"
        } for row in c.fetchall()]
        
        conn.commit()
        return jsonify(messages)
        
    except Exception as e:
        print(f"Error fetching conversation: {str(e)}")
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/my-cars', methods=['GET'])
def my_cars():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    conn = sqlite3.connect('mawater.db')
    c = conn.cursor()
    
    try:
        c.execute("""
            SELECT c.*, COUNT(f.id) as favorite_count
            FROM cars c
            LEFT JOIN favorites f ON f.car_id = c.id
            WHERE c.user_id = ?
            GROUP BY c.id
            ORDER BY c.created_at DESC
        """, (user_id,))
        
        cars = [{
            'id': row[0],
            'make': row[1],
            'model': row[2],
            'year': row[3],
            'price': row[4],
            'mileage': row[5],
            'condition': row[6],
            'description': row[7],
            'status': row[9],
            'created_at': row[10],
            'favorite_count': row[11]
        } for row in c.fetchall()]
        
        return jsonify(cars)
        
    except Exception as e:
        print(f"Error fetching user's cars: {str(e)}")
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/favorites', methods=['GET', 'POST', 'DELETE'])
def favorites():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    conn = sqlite3.connect('mawater.db')
    c = conn.cursor()
    
    if request.method == 'GET':
        try:
            c.execute("""
                SELECT c.*, f.created_at as favorited_at
                FROM cars c
                JOIN favorites f ON c.id = f.car_id
                WHERE f.user_id = ? AND c.status = 'approved'
                ORDER BY f.created_at DESC
            """, (user_id,))
            
            favorites = c.fetchall()
            return jsonify([{
                'id': car[0],
                'make': car[1],
                'model': car[2],
                'year': car[3],
                'price': car[4],
                'mileage': car[5],
                'condition': car[6],
                'description': car[7],
                'favorited_at': car[11]
            } for car in favorites])
            
        except Exception as e:
            print(f"Error fetching favorites: {str(e)}")
            return jsonify({'error': str(e)}), 400
        finally:
            conn.close()
    
    elif request.method == 'POST':
        car_id = request.json.get('car_id')
        if not car_id:
            return jsonify({'error': 'Car ID is required'}), 400
        
        try:
            c.execute("INSERT INTO favorites (user_id, car_id) VALUES (?, ?)",
                     (user_id, car_id))
            conn.commit()
            return jsonify({'message': 'Car added to favorites'})
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Car already in favorites'}), 400
        except Exception as e:
            print(f"Error adding to favorites: {str(e)}")
            return jsonify({'error': str(e)}), 400
        finally:
            conn.close()
    
    elif request.method == 'DELETE':
        car_id = request.args.get('car_id')
        if not car_id:
            return jsonify({'error': 'Car ID is required'}), 400
        
        try:
            c.execute("DELETE FROM favorites WHERE user_id = ? AND car_id = ?",
                     (user_id, car_id))
            conn.commit()
            return jsonify({'message': 'Car removed from favorites'})
        except Exception as e:
            print(f"Error removing from favorites: {str(e)}")
            return jsonify({'error': str(e)}), 400
        finally:
            conn.close()

# Admin routes
@app.route('/api/admin/cars', methods=['GET'])
def admin_cars():
    user_id = request.args.get('user_id')
    status = request.args.get('status')  # Optional status filter
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    conn = sqlite3.connect('mawater.db')
    c = conn.cursor()
    
    try:
        # First check if user is admin
        c.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        
        if not user or not user[0]:
            return jsonify({'error': 'Unauthorized. Admin access required'}), 403
        
        # Get all cars with user information
        query = """
            SELECT c.*, u.firstName, u.lastName, u.email, u.phone
            FROM cars c
            JOIN users u ON c.user_id = u.id
        """
        params = []
        
        # Add status filter if provided
        if status:
            query += " WHERE c.status = ?"
            params.append(status)
            
        query += " ORDER BY c.created_at DESC"
        
        c.execute(query, params)
        cars = c.fetchall()
        
        return jsonify([{
            'id': car[0],
            'make': car[1],
            'model': car[2],
            'year': car[3],
            'price': car[4],
            'mileage': car[5],
            'condition': car[6],
            'description': car[7],
            'user_id': car[8],
            'status': car[9],
            'created_at': car[10],
            'seller_name': f"{car[11]} {car[12]}",
            'seller_email': car[13],
            'seller_phone': car[14]
        } for car in cars])
        
    except Exception as e:
        print(f"Error fetching admin cars: {str(e)}")
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/admin/cars/<int:car_id>', methods=['PUT'])
def admin_update_car(car_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    conn = sqlite3.connect('mawater.db')
    c = conn.cursor()
    
    try:
        # Check if user is admin
        c.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        
        if not user or not user[0]:
            return jsonify({'error': 'Unauthorized. Admin access required'}), 403
        
        data = request.json
        status = data.get('status')
        
        if status not in ['approved', 'rejected']:
            return jsonify({'error': 'Invalid status. Must be approved or rejected'}), 400
        
        # Update car status
        c.execute("""
            UPDATE cars 
            SET status = ?
            WHERE id = ?
        """, (status, car_id))
        
        conn.commit()
        
        return jsonify({
            'message': f'Car {status} successfully',
            'car_id': car_id,
            'status': status
        })
        
    except Exception as e:
        print(f"Error updating car status: {str(e)}")
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
