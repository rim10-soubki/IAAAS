from flask import Flask, request, redirect, render_template
from pymongo import MongoClient
import hashlib

app = Flask(__name__)

# Configuration de la connexion à MongoDB Atlas
client = MongoClient("mailto:mongodb+srv://amaamar01:s013e2ayffviuags@cluster0.1jlmqpc.mongodb.net/")
db = client['<EncryptDB>']  
users_collection = db['Users']

# Fonction pour hasher le mot de passe
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Récupération des données du formulaire
        full_name = request.form['fullName']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        
        # Vérification simple que les mots de passe correspondent
        if password == confirm_password:
            # Hashage du mot de passe
            password_hash = hash_password(password)
            
            # Insérer l'utilisateur dans MongoDB
            user = {
                "fullName": full_name,
                "username": username,
                "passwordHash": password_hash,
                # Ici, vous devriez générer les clés publique/privée
                "publicKey": "user_public_key",
                "privateKeyEncrypted": "encrypted_private_key"
            }
            users_collection.insert_one(user)
            
            # Rediriger l'utilisateur après l'inscription réussie
            return redirect('/success')
        else:
            return "Les mots de passe ne correspondent pas.", 400

    # Si la requête est GET, afficher la page d'inscription (Vous pouvez utiliser des templates Flask)

    return render_template('Front-end/pages/register.html')

@app.route('/success')
def success():
    return "Inscription réussie!"

if __name__ == '__main__':
    app.run(debug=True)
