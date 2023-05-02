import os

# environment variables with credentials
API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
OUTLINE_API_URL = os.environ.get('OUTLINE_API_URL')
# environment variables
LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'ERROR')
AUTHORIZED_IDS = os.environ.get('AUTHORIZED_IDS')
AUTHORIZED_IDS = AUTHORIZED_IDS.split(',') if AUTHORIZED_IDS else ""
