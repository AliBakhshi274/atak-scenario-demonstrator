import asyncio
from configparser import ConfigParser
from geographiclib.geodesic import Geodesic
import pytak
import logging

from model.simulation_model import SimulationManager
from utils.cot_generator import generator_cot_xml


class SimulationController:
    """ 
    Manage the simulation logic, and cooperation between model and view in MVC structure. 
    """
    def __init__(self, config_path: str):
        """ load config """
        self.config = ConfigParser()
        self.config.read(config_path)
        self.cot_url = self.config['cot']['cot_url']

        self.simulation_manager_M = SimulationManager()

        """ simulation state """
        self.is_running = False
        self.sender = None
        self.cli_tool = None

    async def start_simulation(self):
        """ start the simulation """
        if self.is_running:
            return
        
        self.is_running = True
        print("Simulation STARTED ...")

        # Init network tools
        self.cli_tool = pytak.CLITool(config={"COT_URL": self.cot_url})
        await self.cli_tool.setup()

        """ create sample locs """
        fire_loc = (49.877691, 8.657028)
        truck_loc = (49.873091, 8.647028)
        fire_incident = self.simulation_manager_M.add_fire_incident(lat=fire_loc[0], lon=fire_loc[1])
        fire_truck = self.simulation_manager_M.add_fire_truck(lat=truck_loc[0], lon=truck_loc[1])

        route = [
            (49.873091, 8.647028), # Starting point
            (49.875000, 8.650000), # First waypoint
            (49.877000, 8.655000), # Second waypoint
            fire_loc # Destination
        ]

        fire_truck.set_route(route=route)

        self.cli_tool.add_tasks(
            set([MySender(
                self.cli_tool.tx_queue, 
                self.cli_tool.config, 
                self.simulation_manager_M)])
        )

        """ create new Thread for loop in run() """
        self.sender = asyncio.create_task(self.cli_tool.run())


    async def stop_simulation(self):
        """ stop the simulation and cleans up. """
        if not self.is_running:
            print("simulation is not running!")
            return
        
        self.is_running = False
        print("Stopping simulation...")

        if self.sender is not None:
            self.sender.cancel()
            try:
                await self.sender
            except asyncio.CancelledError:
                pass

        if self.cli_tool:
            tasks = list(self.cli_tool.tasks)
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            # clear queue
            self.cli_tool.tx_queue = asyncio.Queue()

class MySender(pytak.QueueWorker):
    def __init__(self, queue, config, simulation_manager):
        super().__init__(queue, config)
        self.simulation_manager = simulation_manager

    async def handle_data(self, data):
        event = data
        await self.put_queue(event)

    async def run(self):
        while True:
            for marker in self.simulation_manager.all_markers():
                data = generator_cot_xml(marker=marker)
                # self._logger.info("Sending:\n%s\n", data.decode())
                await self.handle_data(data)
            await asyncio.sleep(3)
            self.simulation_manager.update_positions()