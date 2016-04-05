# irap_user_server
Simple Django server for interacting with backend running the iRAP pipeline

# installation notes
Running the server requires creating a 'local_settings.py' file in the 'irap_user_server' directory which declares ``EMAIL_HOST_USER = 'user@gmail.com' and EMAIL_HOST_PASSWORD = 'yourpassword'``

This was done to avoid adding sensitive information to version control.