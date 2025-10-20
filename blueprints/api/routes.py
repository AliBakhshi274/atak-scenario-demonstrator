from flask import Blueprint, jsonify
import asyncio
import logging
from datetime import datetime
import threading
from . import api_bp, SIMULATION_CONTROLLER
from utils.decorators import log_block, log_block_async

app_status = {
    'status':'stopped',
    'start_time': None,
}

@api_bp.route('/start', methods=['GET', 'POST'])
def start_simulation():
    
    app_status['status'] = 'start'
    app_status['start_time'] = datetime.now()

    if SIMULATION_CONTROLLER.is_running:
        return jsonify({
            'status': 'Simulation is already running.'
        }), 400

    asyncio.run(SIMULATION_CONTROLLER.start_simulation())

    logging.info("Simulation started via API.")

    return jsonify({
        'status': app_status['status'],
        'message': 'Simulation started successfully, Please Check ATAK client.',
        'start_time': app_status['start_time'].isoformat(),
    }), 200
    

@api_bp.route('/stop', methods=['GET', 'POST'])
def stop_simulation():
    app_status['status'] = 'stopped'

    if not SIMULATION_CONTROLLER.is_running:
        return jsonify({
            'status': 'Simulation is not running.'
        }), 400

    asyncio.run(SIMULATION_CONTROLLER.stop_simulation())

    logging.info("Simulation stopped via API.")

    return jsonify({
        'status': app_status['status'],
        'message': 'Simulation stopped successfully.',
    }), 200

@api_bp.route('/reset', methods=['GET', 'POST'])
def reset_simulation():
    app_status['status'] = 'reset'

    if SIMULATION_CONTROLLER.is_running:
        asyncio.run(SIMULATION_CONTROLLER.stop_simulation())

    asyncio.run(SIMULATION_CONTROLLER.start_simulation())

    logging.info("Simulation reset via API.")

    return jsonify({
        'status': app_status['status'],
        'message': 'Simulation reset successfully.',
    }), 200