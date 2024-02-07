// scripts.js
document.getElementById('loginForm').addEventListener('submit', function(event) {
  event.preventDefault();

  var username = document.getElementById('username').value;
  var password = document.getElementById('password').value;

  console.log("Tentative de connexion avec le nom d'utilisateur", username, "et le mot de passe", password);

});


// register.js
document.getElementById('registerForm').addEventListener('submit', function(event) {
  event.preventDefault();

  var fullName = document.getElementById('fullName').value;
  var username = document.getElementById('username').value;
  var password = document.getElementById('password').value;
  var confirmPassword = document.getElementById('confirmPassword').value;

  if (password !== confirmPassword) {
      alert("Les mots de passe ne correspondent pas.");
      return;
  }

  console.log("Inscription avec le nom complet", fullName, ", nom d'utilisateur", username);

});


    