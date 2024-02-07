from flask import Flask, request, jsonify
import boto3
import jwt  # Install using: pip install pyjwt
from pymongo import MongoClient

app = Flask(__name__)

# Initialize AWS KMS client
kms_client = boto3.client('kms', region_name='your-region')

# Initialize MongoDB client
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['secure_messaging_app']
users_collection = db['users']

# Secret key for JWT token (replace with a secure random key in production)
SECRET_KEY = 'your-secret-key'

@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        full_name = data.get('fullName')
        username = data.get('username')

        # Validate input
        if not full_name or not username:
            return jsonify({'error': 'Full name and username are required'}), 400

        # Check if username already exists
        if users_collection.find_one({'username': username}):
            return jsonify({'error': 'Username already exists'}), 409

        # Generate data key pair using AWS KMS
        response = kms_client.generate_data_key(
            KeyId='your-kms-key-id',  # ID or ARN of the AWS KMS key
            KeySpec='RSA_2048'
        )

        # Extract encrypted and plaintext data keys
        encrypted_data_key = response['CiphertextBlob']
        plaintext_data_key = response['Plaintext']

        # Save user information and encrypted data key to the database
        user_data = {'full_name': full_name, 'username': username, 'encrypted_data_key': encrypted_data_key}
        users_collection.insert_one(user_data)

        # Generate JWT token for user authentication
        token = jwt.encode({'username': username}, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'message': 'User registered successfully', 'token': token}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
