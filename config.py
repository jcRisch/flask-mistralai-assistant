import os

class Config:
    FLASK_DEBUG=os.getenv("FLASK_DEBUG")
    MISTRALAI_KEY = os.getenv('MISTRALAI_KEY')