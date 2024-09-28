# Dette er det samme kode som i app.ipynb, forskellen er bare filformatet.
from data_dict import random_users
from flask import Flask, jsonify, request
import faker
import sqlite3
import os

GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect('members.db')
    return conn


def create_table():
    conn = connect_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS members (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        birth_date TEXT NOT NULL,
                        gender TEXT NOT NULL,
                        email TEXT,
                        phonenumber TEXT,
                        address TEXT,
                        nationality TEXT,
                        active INTEGER NOT NULL CHECK (active IN (0, 1)),
                        github_username TEXT)''')
    conn.commit()
    conn.close()

create_table()

def add_faker_users():
    conn = connect_db()
    cursor = conn.execute("SELECT * FROM members")
    members = cursor.fetchall()
    data = random_users
    if len(members)>10:
        return
    
    members_data = [(user['first_name'], user['last_name'], user['birth_date'], user['gender'], 
                           user['email'], user['phonenumber'], user['address'], user['nationality'], 
                           user['active'], user['github_username']) for user in data]

    cursor = conn.executemany('''INSERT INTO members 
                          (first_name, last_name, 
                          birth_date, gender, email, 
                          phonenumber, address, nationality, 
                          active, github_username)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        members_data)
    
    conn.commit()
    conn.close()

add_faker_users()

@app.route('/members', methods=['GET'])
def index():
    conn = connect_db()
    cursor = conn.execute("SELECT * FROM members")
    members = cursor.fetchall()


    return jsonify(members)

@app.route('/members', methods=['POST'])
def create():
    conn = connect_db()
    data = request.get_json()
    
    cursor = conn.execute('''INSERT INTO members 
                          (first_name, last_name, 
                          birth_date, gender, email, 
                          phonenumber, address, nationality, 
                          active, github_username)
                          VALUES (?, ?, ?, ?, ?, ?git commit -m "Initial commit"
, ?, ?, ?, ?)''', 
                          (data['first_name'], data['last_name'], data['birth_date'], data['gender'], 
                           data['email'], data['phonenumber'], data['address'], data['nationality'], 
                           data['active'], data['github_username']))
    
    conn.commit()
    conn.close()

    new_member = {
        "github_username": data['github_username'] 
    }
    
    return jsonify(new_member), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    conn = connect_db()
    data = request.get_json()
    cursor = conn.execute('SELECT * FROM members WHERE id=?', (id,))
    member = cursor.fetchone()
    if member is None:
        return jsonify({"error": "Member not found"}), 404
    
    conn.execute('''UPDATE members SET
                          first_name=?, last_name=?, 
                          birth_date=?, gender=?, email=?, 
                          phonenumber=?, address=?, nationality=?, 
                          active=?, github_username=? WHERE id=?''', 
                          (data['first_name'], data['last_name'], data['birth_date'], data['gender'], 
                           data['email'], data['phonenumber'], data['address'], data['nationality'], 
                           data['active'], data['github_username'], id))
    
    conn.commit()
    conn.close()
    
    updated_member = {
        "github_username": data['github_username'] 
    }
    
    return jsonify(updated_member), 200

@app.route('/members/<int:id>', methods=['Patch'])
def patchy(id):
    conn = connect_db()

    cursor = conn.execute('SELECT * FROM members WHERE id=?', (id,))
    member = cursor.fetchone()
    if member is None:
        return jsonify({"error": "Member not fond"}), 404
    data = request.get_json()   

    first_name = data.get('first_name', member[1])
    last_name = data.get('last_name', member[2])
    birth_date = data.get('birth_date', member[3])
    gender = data.get('gender', member[4])
    email = data.get('email', member[5])
    phonenumber = data.get('phonenumber', member[6])
    address = data.get('address', member[7])
    nationality = data.get('nationality', member[8])
    active = data.get('active', member[9])
    github_username = data.get('github_username', member[10])


    conn.execute('''UPDATE members SET 
                    first_name=?, last_name=?, birth_date=?, gender=?, email=?, 
                    phonenumber=?, address=?, nationality=?, active=?, github_username=?
                    WHERE id=?''',
                 (first_name, last_name, birth_date, gender, email, 
                  phonenumber, address, nationality, active, github_username, id))
    conn.commit()
    conn.close()
    updated_member = {
        "github_username": github_username
    }

    return jsonify(updated_member), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def remove(id):
    conn = connect_db()
    data = request.get_json()
    cursor = conn.execute('SELECT * FROM members WHERE id=?', (id,))
    member = cursor.fetchone()
    if member is None:
        return jsonify({"error": "Member not found"}), 404
    
    conn.execute('DELETE FROM members WHERE id=?',(id))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "member  deleted"}), 200

@app.route('/delete_table', methods=['DELETE'])
def delete_table():
    conn = connect_db()
    conn.execute('DROP TABLE IF EXISTS members')  
    conn.commit()
    conn.close()
    return jsonify({"message": "Table  deleted"}), 200

if __name__ == "__main__":
    app.run()