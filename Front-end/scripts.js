$(document).ready(function() {
    // Handle registration form submission
    $('#registrationForm').submit(function(e) {
      e.preventDefault();
      var formData = $(this).serialize();
      $.ajax({
        type: 'POST',
        url: '/register',
        data: formData,
        success: function(response) {
          alert(response.message);
          $('#registrationForm')[0].reset();
        },
        error: function(error) {
          alert(error.responseJSON.error);
        }
      });
    });
    
    // Handle message sending form submission
    $('#sendMessageForm').submit(function(e) {
      e.preventDefault();
      var formData = $(this).serialize();
      $.ajax({
        type: 'POST',
        url: '/send_message',
        data: formData,
        success: function(response) {
          alert(response.message);
          $('#sendMessageForm')[0].reset();
        },
        error: function(error) {
          alert(error.responseJSON.error);
        }
      });
    });
    
    // Function to fetch
  