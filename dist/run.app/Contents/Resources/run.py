# run.py
from dotenv import load_dotenv
load_dotenv()  # Prends les variables d'environnement depuis .env.

from app import app

if __name__ == '__main__':
    app.run(debug=True)
