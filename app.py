from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

@app.route('/user', methods=['GET'])
def get_users():
    users = load_users()
    # Filtros
    name = request.args.get('name')
    role = request.args.get('role')
    is_active = request.args.get('is_active')

    if name:
        users = [user for user in users if name.lower() in user['username'].lower()]
    if role:
        users = [user for user in users if user['role'] == role]
    if is_active is not None:
        is_active = is_active.lower() == 'true'
        users = [user for user in users if user['is_active'] == is_active]

    return jsonify(users)

@app.route('/user', methods=['POST'])
def create_user():
    users = load_users()
    data = request.get_json()

    if not data.get('email'):
        return jsonify({"error": "Email is required"}), 400

    if any(user['email'] == data['email'] for user in users):
        return jsonify({"error": "User with this email already exists"}), 400

    new_user = {
        "username": data.get('username'),
        "email": data['email'],
        "is_active": data.get('is_active', True),
        "created_at": datetime.now().isoformat(),
        "role": data.get('role', 'user')
    }

    users.append(new_user)
    save_users(users)
    return jsonify(new_user), 201

@app.route('/user/<email>', methods=['DELETE'])
def delete_user(email):
    users = load_users()
    user_to_delete = next((user for user in users if user['email'] == email), None)

    if not user_to_delete:
        return jsonify({"error": "User not found"}), 404

    users.remove(user_to_delete)
    save_users(users)
    return jsonify({"message": "User deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
