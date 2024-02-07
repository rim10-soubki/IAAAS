from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)

# Initialize AWS KMS client
kms_client = boto3.client('kms', region_name='your-region')

@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        full_name = data.get('fullName')
        username = data.get('username')

        # Validate input
        if not full_name or not username:
            return jsonify({'error': 'Full name and username are required'}), 400

        # Generate data key pair using AWS KMS
        response = kms_client.generate_data_key(
            KeyId='your-kms-key-id',  # ID or ARN of the AWS KMS key
            KeySpec='RSA_2048'
        )

        # Extract encrypted and plaintext data keys
        encrypted_data_key = response['CiphertextBlob']
        plaintext_data_key = response['Plaintext']

        # Save user information and encrypted data key to the database
        # (Replace this with your actual database implementation)
        save_user_to_database(full_name, username, encrypted_data_key)

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def save_user_to_database(full_name, username, encrypted_data_key):
    # Implement your code to save user information and encrypted data key to the database
    # Example: Store the user's full name, username, and encrypted data key in MongoDB
    # (Replace this with your actual database implementation)
    pass

if __name__ == '__main__':
    app.run(debug=True)
