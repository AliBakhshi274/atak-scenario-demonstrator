'''
flask --app __init__.py run --debugg
'''

import logging

# Clear existing logging handlers (it's important to avoid duplicate logs)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# logging.basicConfig(level=logging.INFO)

# from view.SimulationGUI import SimulationGUI

# def main():
#     app = SimulationGUI()
#     app.mainloop()

# if __name__ == "__main__":
#     try:
#         main()
#     except (KeyboardInterrupt, SystemExit):
#         print("Program terminated.")


from flask import Flask
from blueprints.api import api_bp
from controller.simulation_controller import SimulationController


def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

