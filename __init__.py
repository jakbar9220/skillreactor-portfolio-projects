from flask import Flask, request, jsonify
import boto3
import hashlib
from flask_cors import CORS

import jwt
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

api = Flask(__name__)
CORS(api)  # Enable CORS for all routes

# Load environment variables from .env file (.env file is tobe created manually in root folder)
load_dotenv()

# Access the environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
secretKey = os.getenv('JWT_SECRET_KEY')


session = boto3.Session(  
    aws_access_key_id=aws_access_key_id,  
    aws_secret_access_key=aws_secret_access_key,  
    region_name='eu-west-2'  
)  
      
dynamodb = session.resource('dynamodb')

table_name = 'userauthenticationapi_user_j-akbar'

def get_user_data_from_dynamodb(username):
    table = dynamodb.Table(table_name)
    response = table.get_item(Key={'username': username})
    item = response.get('Item')
    if item:
        return {item['username']: item['password']}
    else:
        return {}

# USER_DATA = get_user_data_from_dynamodb("JowhnW")


@api.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validate input
    if not username or not email or not password:
        return jsonify({'message': 'Username, email, and password are required'}), 400

    # Hash the password with SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Save user data to DynamoDB
    table = dynamodb.Table(table_name)
    table.put_item(Item={'username': username, 'email': email, 'password': hashed_password})

    response = jsonify({'message': 'User registered successfully'})
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow all origins
    response.headers.add('Access-Control-Allow-Methods', '*')  # Allow POST and OPTIONS methods
    return response, 201


@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user_data = get_user_data_from_dynamodb(username)

    if user_data and user_data.get(username) == hashlib.sha256(password.encode()).hexdigest():
        expirationTime = datetime.utcnow() + timedelta(hours=2)  
        token = jwt.encode({'username': username, 'exp': expirationTime}, secretKey)
        return token
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@api.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    print(token)
    if token is None:
        return jsonify({'error': 'No Authorization header provided'}), 401
    
    auth_type, token_value = token.rsplit(' ', 1)
    print(token_value)
    print(auth_type)
    if auth_type.lower() != 'bearer':
        return jsonify({'error': 'Invalid Authorization header format'}), 403

    try:  
        decoded = jwt.decode(token_value, secretKey, algorithms=['HS256'])  
    except jwt.InvalidTokenError:  
        return jsonify({'error': 'Invalid Token'}), 403

    return "Hello"


@api.route("/")
def welcome():
    return "Welcome to SkillReactor"
