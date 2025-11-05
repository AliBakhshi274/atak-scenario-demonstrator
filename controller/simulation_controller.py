import asyncio
from configparser import ConfigParser
from geographiclib.geodesic import Geodesic
import pytak
import logging

from model.simulation_model import FireTruck, SimulationManager
from utils.cot_generator import generator_cot_xml
from utils.decorators import log_block_async, log_block

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

    # @log_block_async
    async def start_simulation(self):
        """ start the simulation """
        try:
            if self.is_running:
                logging.warning("simulation is already running!")
                await self.stop_simulation()
                # Reset simulation state
                self.simulation_manager_M = SimulationManager()
        
            self.is_running = True

            # Init network tools
            self.cli_tool = pytak.CLITool(config={"COT_URL": self.cot_url})
            await self.cli_tool.setup()

            """ create sample locs """
            fire_loc = (49.877691, 8.657028)
            truck_1_loc = (49.873091, 8.647028)
            truck_2_loc = (49.879091, 8.637028)

            fire_incident = self.simulation_manager_M.add_fire_incident(lat=fire_loc[0], lon=fire_loc[1])
            fire_truck_1 = self.simulation_manager_M.add_fire_truck(lat=truck_1_loc[0], lon=truck_1_loc[1])
            fire_truck_2 = self.simulation_manager_M.add_fire_truck(lat=truck_2_loc[0], lon=truck_2_loc[1])

            route_fire_truck_1 = [
                (49.873091, 8.647028), # Starting point
                (49.875000, 8.650000), # First waypoint
                (49.877000, 8.655000), # Second waypoint
                fire_loc # Destination
            ]

            route_fire_truck_2 = [
                (49.879091, 8.637028), # Starting point
                (49.878091, 8.647028), # First waypoint
                (49.876800, 8.660000), # Second waypoint
                (49.877000, 8.655000), # Third waypoint
                fire_loc # Destination
            ]

            fire_truck_1.set_route(route=route_fire_truck_1)
            fire_truck_2.set_route(route=route_fire_truck_2)

            self.sender_task = MySender(
                queue=self.cli_tool.tx_queue,
                config=self.cli_tool.config,
                simulation_manager=self.simulation_manager_M
            )
            self.cli_tool.add_tasks(
                set([self.sender_task])
            )

            """ create new Thread for loop in run() """
            self.sender = asyncio.create_task(self.cli_tool.run())

            await self.sender
        except asyncio.CancelledError:
            logging.info("Simulation was cancelled.")
            await self._cleanup()
            # await self.cli_tool.close()
            # self.cli_tool = None
            # self.sender = None
            # self.sender_task = None
            # self.cli_tool = None
        except Exception as e:
            logging.error(f"Error in start_simulation: {e}")
            await self._cleanup()

    # @log_block_async
    # async def stop_simulation(self):
    #     """ stop the simulation and cleans up. """
    #     if not self.is_running:
    #         print("simulation is not running!")
    #         return
        
    #     self.is_running = False

    #     if hasattr(self, 'sender_task'):
    #         self.sender_task.stop()

    #     if self.sender is not None:
    #         self.sender.cancel()
    #         try:
    #             await self.sender
    #         except asyncio.CancelledError:
    #             pass

    #     if self.cli_tool:
    #         for task in list(self.cli_tool.tasks):
    #             task.cancel()
    #             task = None
    #         await asyncio.gather(*self.cli_tool.tasks, return_exceptions=True)
    #         # clear queue
    #         self.cli_tool.tx_queue = asyncio.Queue()
    #         self.cli_tool = None
    #         self.sender = None
    #         self.sender_task = None

    async def stop_simulation(self):
        """ stop the simulation and cleans up. """
        if not self.is_running:
            print("simulation is not running!")
            return
        
        self.is_running = False
        await self._cleanup()


    async def _cleanup(self):
        """Cleanup resources"""
        try:
            # stop sender_task
            if hasattr(self, 'sender_task') and self.sender_task:
                self.sender_task.stop()
                self.sender_task = None

            if self.sender and not self.sender.done():
                self.sender.cancel()
                try:
                    await asyncio.wait_for(self.sender, timeout=2.0)  # اضافه کردن timeout
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                self.sender = None

            # cleanup cli_tool
            if self.cli_tool:
                if hasattr(self.cli_tool, 'tasks'):
                    tasks_to_cancel = [task for task in self.cli_tool.tasks if not task.done()]
                    for task in tasks_to_cancel:
                        task.cancel()
                    
                    if tasks_to_cancel:
                        try:
                            await asyncio.wait_for(asyncio.gather(*tasks_to_cancel, return_exceptions=True), timeout=3.0)
                        except asyncio.TimeoutError:
                            pass
                
                self.cli_tool.tx_queue = asyncio.Queue()
                self.cli_tool = None
                
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
            
class MySender(pytak.QueueWorker):
    def __init__(self, queue, config, simulation_manager: SimulationManager):
        super().__init__(queue, config)
        self.simulation_manager = simulation_manager
        self.sending = True

    def stop(self):
        self.sending = False
        
    async def handle_data(self, data):
        event = data
        await self.put_queue(event)

    # @log_block_async
    async def run(self):
        while self.sending:
            for marker in self.simulation_manager.all_markers():
                # it's not working as expected (marker need to be exactly on the last point)
                # if isinstance(marker, FireTruck) and marker.has_arrived():
                #     print(f"{marker.uid} has arrived at destination.")
                #     continue
                data = generator_cot_xml(marker=marker)
                # self._logger.info("Sending:\n%s\n", data.decode())
                await self.handle_data(data)
            await asyncio.sleep(0.08)  # Adjust the sleep duration as needed
            self.simulation_manager.update_positions()
