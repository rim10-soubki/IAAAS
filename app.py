from flask import Flask, request, redirect, render_template, session, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from cryptography.fernet import Fernet, InvalidToken
from flask_socketio import SocketIO, emit
from datetime import datetime
import hashlib
import os

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = os.urandom(24)  # Pour la production, utilisez une clé fixe définie dans un environnement sécurisé

# Remplacez ceci par votre propre chaîne de connexion à MongoDB Atlas
client = MongoClient("mongodb+srv://amaamar01:s013e2aYFFVIUAGs@cluster0.1jlmqpc.mongodb.net/?retryWrites=true&w=majority")
db = client['EncryptDB']
users_collection = db['Users']
messages_collection = db['messages']

key = os.environ.get('FERNET_KEY')  
if key is None:
    raise ValueError("La clé Fernet n'est pas définie dans les variables d'environnement.")
cipher_suite = Fernet(key.encode('utf-8'))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def encrypt_message(message):
    if isinstance(message, str):
        message = message.encode()  # Convertit en bytes si nécessaire
    encrypted_message = cipher_suite.encrypt(message)
    return encrypted_message.decode()  # Stockez et travaillez avec le message chiffré en tant que string

def decrypt_message(encrypted_message):
    try:
        decrypted_message = cipher_suite.decrypt(encrypted_message.encode())
        return decrypted_message.decode()
    except InvalidToken:
        raise ValueError("Le message ne peut pas être déchiffré avec la clé fournie.")

# Ajoutez cette fonction pour la rendre accessible depuis les templates Jinja2
@app.context_processor
def utility_processor():
    return dict(decrypt_message=decrypt_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['fullName']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        
        if password == confirm_password:
            password_hash = hash_password(password)
            user = {"fullName": full_name, "username": username, "passwordHash": password_hash}
            users_collection.insert_one(user)
            return redirect(url_for('login'))
        else:
            flash('Les mots de passe ne correspondent pas.', 'danger')
    
    return render_template('front-end/pages/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({"username": username})
        
        if user and user['passwordHash'] == hash_password(password):
            session['user_id'] = str(user['_id'])
            session['username'] = username
            return redirect(url_for('send_message'))
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect', 'danger')
    
    return render_template('front-end/pages/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    if 'username' not in session:
        flash("Vous devez être connecté pour envoyer un message.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        receiver_username = request.form['receiverUsername']
        message_content = request.form['messageContent']
        receiver = users_collection.find_one({"username": receiver_username})
        
        if receiver:
            encrypted_message = encrypt_message(message_content)
            messages_collection.insert_one({
                "senderId": ObjectId(session['user_id']),
                "receiverId": receiver['_id'],
                "messageEncrypted": encrypted_message,
                "timestamp": datetime.utcnow(),
                "read": False
            })
            flash("Message envoyé avec succès.", "success")
        else:
            flash("Destinataire non trouvé.", "danger")
    
    users = users_collection.find({"_id": {"$ne": ObjectId(session['user_id'])}})
    return render_template('front-end/pages/sendMessage.html', users=list(users))

def get_conversations_for_user(user_id):
    user_id = ObjectId(user_id)
    conversations = []

    user_conversations = messages_collection.aggregate([
        {"$match": {"$or": [{"senderId": user_id}, {"receiverId": user_id}]}},
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": {
                "$cond": {
                    "if": {"$eq": ["$senderId", user_id]},
                    "then": "$receiverId",
                    "else": "$senderId"
                }
            },
            "last_message": {"$first": "$$ROOT"}
        }},
        {"$lookup": {
            "from": users_collection.name,
            "localField": "_id",
            "foreignField": "_id",
            "as": "other_user"
        }},
        {"$unwind": "$other_user"}
    ])

    for convo in user_conversations:
        other_user = convo['other_user']
        last_message = convo['last_message']
        conversations.append({
            "other_user_id": str(other_user['_id']),
            "other_username": other_user['username'],
            "last_message_content": decrypt_message(last_message['messageEncrypted']),
            "last_message_timestamp": last_message['timestamp']
        })

    return conversations

@app.route('/messages')
def messages():
    if 'user_id' not in session:
        flash("Vous devez être connecté pour voir les messages.", "warning")
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    conversations = get_conversations_for_user(user_id)
    return render_template('front-end/pages/messagesHistory.html', conversations=conversations)

def get_messages_with_user(user_id, other_user_id):
    user_id = ObjectId(user_id)
    other_user_id = ObjectId(other_user_id)
    messages = list(messages_collection.find({
        "$or": [
            {"senderId": user_id, "receiverId": other_user_id},
            {"senderId": other_user_id, "receiverId": user_id}
        ]
    }).sort("timestamp", 1))  # Assurez-vous que ce tri est correct selon votre modèle de données
    return messages

@app.route('/conversation/<other_user_id>')
def conversation(other_user_id):
    if 'user_id' not in session:
        flash("Vous devez être connecté pour voir cette conversation.", "warning")
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    messages = get_messages_with_user(user_id, other_user_id)
    other_user = users_collection.find_one({"_id": ObjectId(other_user_id)})
    other_username = other_user['username'] if other_user else 'Utilisateur Inconnu'
    sender_full_name = other_user['fullName'] if other_user else 'Expéditeur Inconnu'
    
    return render_template('front-end/pages/conversation.html', messages=messages, other_username=other_username, sender_full_name=sender_full_name, user_id=user_id)

from flask import jsonify

@app.route('/send_message_ajax', methods=['POST'])
def send_message_ajax():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Vous devez être connecté pour envoyer un message."})

    sender_username = session['username']
    sender = users_collection.find_one({"username": sender_username})  # Récupérer l'utilisateur complet
    receiver_username = request.form['receiverUsername']
    message_content = request.form['messageContent']

    receiver = users_collection.find_one({"username": receiver_username})
    if receiver and sender:
        encrypted_message = encrypt_message(message_content)
        
        # Ajouter le nom complet de l'expéditeur
        sender_full_name = sender['fullName']
        
        messages_collection.insert_one({
            "senderId": ObjectId(session['user_id']),
            "senderFullName": sender_full_name,  # Ajouter le nom complet de l'expéditeur
            "receiverId": receiver['_id'],
            "messageEncrypted": encrypted_message,
            "timestamp": datetime.utcnow(),
            "read": False
        })
        return jsonify({"success": True, "message": "Message envoyé avec succès."})
    else:
        return jsonify({"success": False, "message": "Destinataire ou expéditeur non trouvé."})


def handle_message(data):
    # Envoyer le message reçu à tous les clients sauf l'émetteur
    emit('message_received', data, broadcast=True, include_self=False)

def conversation():
    return render_template('conversation.html')

if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app)
