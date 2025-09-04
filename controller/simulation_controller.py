import asyncio
from configparser import ConfigParser
from geographiclib.geodesic import Geodesic
import pytak

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
        self.cli_tool = pytak.CLITool({"COT_URL": self.cot_url})
        await self.cli_tool.setup()

        """ create sample locs """
        fire_loc = (49.877691, 8.657028)
        truck_loc = (49.873091, 8.647028)
        self.simulation_manager_M.add_fire_incident(lat=fire_loc[0], lon=fire_loc[1])
        self.simulation_manager_M.add_fire_truck(lat=truck_loc[0], lon=truck_loc[1])

        self.sender = asyncio.create_task(self._send_loop())

    async def stop_simulation(self):
        """ stop the simulation and cleans up. """
        if not self.is_running:
            return
        
        self.is_running = False
        print("simulation STOPPED!")

        if self.sender:
            self.sender.cancel()

        if self.cli_tool:
            await self.cli_tool.close()

    async def _send_loop(self):
        """ async loop for sending data """
        while True:
            for marker in self.simulation_manager_M.all_markers():
                cot_xml = generator_cot_xml(marker=marker)
                self.cli_tool.tx_queue.put_nowait(cot_xml)
                # implement sending of cot_xml to the COT server
            await asyncio.sleep(5)