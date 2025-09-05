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
        self.cli_tool = pytak.CLITool(config={"COT_URL": self.cot_url})
        await self.cli_tool.setup()

        """ create sample locs """
        fire_loc = (49.877691, 8.657028)
        truck_loc = (49.873091, 8.647028)
        self.simulation_manager_M.add_fire_incident(lat=fire_loc[0], lon=fire_loc[1])
        self.simulation_manager_M.add_fire_truck(lat=truck_loc[0], lon=truck_loc[1])

        # self.sender = asyncio.create_task(self._send_loop())

        self.cli_tool.add_tasks(
               set([MySender(
                   self.cli_tool.tx_queue, 
                   self.cli_tool.config, 
                   self.simulation_manager_M
                   )])
               )

        await self.cli_tool.run()

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

    # async def _send_loop(self, queue_worker: pytak.QueueWorker):
    #     super().__init__(queue_worker)
    #     """ async loop for sending data """
    #     while True:
    #         for marker in self.simulation_manager_M.all_markers():
    #             cot_xml = generator_cot_xml(marker=marker)
    #             await queue_worker.put_queue(cot_xml)
    #         await asyncio.sleep(3)

    # async def _send_loop(self):
    #     """ async loop for sending data """
    #     while True:
    #         for marker in self.simulation_manager_M.all_markers():
    #             cot_xml = generator_cot_xml(marker=marker)
    #             # print(cot_xml.decode())
    #             self.cli_tool.tx_queue.put_nowait(cot_xml)
    #         self.cli_tool.add_task(
    #             set([pytak.QueueWorker(self.cli_tool.tx_queue, self.cli_tool.config)])
    #         )
    #         await asyncio.sleep(5)
    #     # print(".............................................................")

class MySender(pytak.QueueWorker):
    def __init__(self, queue, config, simulation_manager):
        super().__init__(queue, config)
        self.simulation_manager = simulation_manager

    async def handle_data(self, data):
        event = data
        await self.put_queue(event)

    async def run(self):
        while True:
            marker = self.simulation_manager.get_marker_by_uid(uid="fire-truck-1")
            print(marker)
            data = generator_cot_xml(marker=marker)
            print(f"..........{data}..........")
            await self.handle_data(data)
            await asyncio.sleep(1)