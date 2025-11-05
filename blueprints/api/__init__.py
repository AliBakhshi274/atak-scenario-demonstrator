from flask import Blueprint
from controller.simulation_controller import SimulationController

api_bp = Blueprint('api', __name__, url_prefix='/api', template_folder='templates')

SIMULATION_CONTROLLER = SimulationController(config_path="config/settings.ini")

from . import routes
