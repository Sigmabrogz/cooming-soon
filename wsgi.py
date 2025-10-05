"""
WSGI entry point for production deployment
"""
from app import app

# Vercel requires the app to be named 'app'
if __name__ == "__main__":
    app.run()
