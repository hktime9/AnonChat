# AnonChat
An anonymous group chatting application
This is based on the Python Flask-Socketio framework
It uses a textfile "nicknamesList.txt" to get a list
of unique nicknames to give to each client. Nicknames
are given according to the IP address of each client.
The app supports emojis and has a blacklist policy 
against violators. It is safe against <script> tag 
injection.
