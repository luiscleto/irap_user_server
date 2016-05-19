# irap_user_server
Simple Django server for interacting with backend running the iRAP pipeline

# installation notes
Django must be installed from django-nonrel (using the command):

```pip install git+https://github.com/django-nonrel/django@nonrel-1.6```


Running the server requires creating a 'local_settings.py' file in the 'irap_user_server' directory which declares ``EMAIL_HOST_USER = 'user@gmail.com'`` and ``EMAIL_HOST_PASSWORD = 'yourpassword'``

This was done to avoid adding sensitive information to version control.


Additionally, 'local_settings.py' should also declare the following variables:
 - ``FRONT_END_SERVER_ADDRESS``: address for the server where the website will be hosted
 - ``IRAP_SERVER_ADDRESS``: address for the cluster server where iRAP is installed
 - ``MAX_NUMBER_OF_PROCESSES``: size of worker process pool (only relevant for the cluster server)
 - ``IRAP_DIR``: work directory of the iRAP program, should be the same as the $IRAP_DIR environment variable (only relevant for the cluster server)

