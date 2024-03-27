from flask import Flask
from config import Config
import logging

from .routes.domotics import domotics_bp
from .routes.assistant import assistant_bp

from .services.domotics import DomoticsService

domotic_data = {
    1: {'zone': 'kitchen', 'devices': {'light': True, 'door': False}},
    2: {'zone': 'outdoor', 'devices': {'light': True, 'camera': True}},
}

def create_app(config_class=Config):
    app = Flask(__name__)
    app.secret_key = 'super_secret_key'
    app.config.from_object(config_class)
    app.logger.setLevel(logging.INFO)
    app.register_blueprint(domotics_bp)
    app.register_blueprint(assistant_bp)
    
    app.domotics_service = DomoticsService(domotic_data)

    return app