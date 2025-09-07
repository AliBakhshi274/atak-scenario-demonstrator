import asyncio

from controller.simulation_controller import SimulationController


async def main():
    
    controller = SimulationController(config_path="config/settings.ini")

    await controller.start_simulation()

    try:
        while True:
            print("wait for 1 min...")
            await asyncio.sleep(1)
            await controller.stop_simulation()
    except asyncio.CancelledError:
        pass
    # except KeyboardInterrupt:
    #     print("Stopping simulation...")
    #     await controller.stop_simulation()
        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Program terminated.")
