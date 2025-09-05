import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from controller.simulation_controller import SimulationController


async def main():
    
    controller = SimulationController(config_path="config/settings.ini")

    await controller.start_simulation()

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print("Stopping simulation...")
        await controller.stop_simulation()
        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Program terminated.")
