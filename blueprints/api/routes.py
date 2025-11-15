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

    run_async(SIMULATION_CONTROLLER.start_simulation())

    logging.info("Simulation started viaa API.")

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

    try:
        run_async(SIMULATION_CONTROLLER.stop_simulation())
        logging.info("Simulation stopped via API.")
        
        return jsonify({
            'status': app_status['status'],
            'message': 'Simulation stopped successfully.',
        }), 200
    except Exception as e:
        logging.error(f"Error stopping simulation: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error stopping simulation: {str(e)}'
        }), 500

@api_bp.route('/reset', methods=['GET', 'POST'])
def reset_simulation():
    app_status['status'] = 'reset'

    try:
        if SIMULATION_CONTROLLER.is_running:
            run_async(SIMULATION_CONTROLLER.reset_simulation())
        
        import time
        time.sleep(1)
        
        # run_async(SIMULATION_CONTROLLER.start_simulation())

        logging.info("Simulation reset via API.")

        return jsonify({
            'status': app_status['status'],
            'message': 'Simulation reset successfully.',
        }), 200
    except Exception as e:
        logging.error(f"Error resetting simulation: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error resetting simulation: {str(e)}'
        }), 500


def run_async(corotask):
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                result = new_loop.run_until_complete(corotask)
                new_loop.close()
                return result
            except Exception as e:
                new_loop.close()
                raise e
        else:
            return loop.run_until_complete(corotask)
            
    except Exception as e:
        logging.error(f"Error in run_async: {e}")
        raise e