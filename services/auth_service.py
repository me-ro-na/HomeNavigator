from flask import Blueprint, request, jsonify

auth_service = Blueprint('auth_service', __name__)

# 예시 사용자 자격 증명
users = {'user@example.com': 'password123'}

@auth_service.route('/perform_login', methods=['POST'])
def perform_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if email in users and users[email] == password:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure'})
