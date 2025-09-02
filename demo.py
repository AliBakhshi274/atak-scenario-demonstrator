#!/usr/bin/env python3

import asyncio
import xml.etree.ElementTree as ET
import pytak

from configparser import ConfigParser

from geographiclib.geodesic import Geodesic
geod = Geodesic.WGS84


loc_center = (49.877691, 8.657028)
current_phi = 0.0


def gen_cot():
    global current_phi
    """Generate CoT Event."""
    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", "a-h-A-M-A")  # insert your type of marker
    root.set("uid", "demo_test_pc_to_atak")
    root.set("how", "m-g")
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set(
        "stale", pytak.cot_time(60)
    )  # time difference in seconds from 'start' when stale initiates

    current_phi += (90 / 4)
    current_phi %= 360

    new_pos = geod.Direct(loc_center[0], loc_center[1], current_phi, 10)

    pt_attr = {
        "lat": f"{new_pos['lat2']:.8f}",  # set your lat (this loc points to Central Park NY)
        "lon": f"{new_pos['lon2']:.8f}",  # set your long (this loc points to Central Park NY)
        "hae": "0",
        "ce": "10",
        "le": "10",
    }

    ET.SubElement(root, "point", attrib=pt_attr)

    return ET.tostring(root)


class MySender(pytak.QueueWorker):
    """
    Defines how you process or generate your Cursor-On-Target Events.
    From there it adds the COT Events to a queue for TX to a COT_URL.
    """

    async def handle_data(self, data):
        """Handle pre-CoT data, serialize to CoT Event, then puts on queue."""
        event = data
        await self.put_queue(event)

    async def run(self):
        """Run the loop for processing or generating pre-CoT data."""
        while True:
            data = gen_cot()
            self._logger.info("Sending:\n%s\n", data.decode())
            await self.handle_data(data)
            await asyncio.sleep(1)


class MyReceiver(pytak.QueueWorker):
    """Defines how you will handle events from RX Queue."""

    async def handle_data(self, data):
        """Handle data from the receive queue."""
        try:
            self._logger.info("Received:\n%s\n", data.decode())
        except UnicodeDecodeError as e:
            self._logger.warning("Could not decode received data:\n%s", e)

    async def run(self):
        """Read from the receive queue, put data onto handler."""
        while True:
            data = (
                await self.queue.get()
            )  # this is how we get the received CoT from rx_queue
            await self.handle_data(data)


async def main():
    """Main definition of your program, sets config params and
    adds your serializer to the asyncio task list.
    """
    config = ConfigParser()
    config["mycottool"] = {"COT_URL": "udp://239.2.3.1:6969"}
    config = config["mycottool"]

    # Initializes worker queues and tasks.
    clitool = pytak.CLITool(config)
    await clitool.setup()

    # Add your serializer to the asyncio task list.
    clitool.add_tasks(
        set([MySender(clitool.tx_queue, config), MyReceiver(clitool.rx_queue, config)])
    )

    # Start all tasks.
    await clitool.run()


if __name__ == "__main__":
    asyncio.run(main())
