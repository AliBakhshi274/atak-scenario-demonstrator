import xml.etree.ElementTree as ET
import pytak

from model.simulation_model import Marker


def generator_cot_xml(marker: Marker):
    """
    Generates Cursor-On-Target XML for a given Marker object.
    """
    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", marker.type)
    root.set("uid", marker.uid)
    root.set("how", "m-g")
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set(
        "stale", pytak.cot_time(60)
    )  # time difference in seconds from 'start' when stale initiates

    pt_attr = {
        "lat": f"{marker.lat:.8f}",
        "lon": f"{marker.lon:.8f}",
        "hae": "0",
        "ce": "10",
        "le": "10",
    }
    ET.SubElement(root, "point", attrib=pt_attr)

    return ET.tostring(root)