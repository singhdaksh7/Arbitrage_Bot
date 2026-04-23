"""Routes package"""

from flask import Blueprint

api_bp = Blueprint('api', __name__)
web_bp = Blueprint('web', __name__)

from app.routes import api, web
