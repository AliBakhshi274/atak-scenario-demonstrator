import xml.etree.ElementTree as ET
import pytak
from geographiclib.geodesic import Geodesic

from model.simulation_model import Marker

geod = Geodesic.WGS84

loc_center = (49.877691, 8.657028)
current_phi = 0.0

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

# """ cot = cursor_on_target """
# def cot_get():
#     global current_phi
#     """Generate CoT Event."""
#     root = ET.Element("event")
#     root.set("version", "2.0")
#     root.set("type", "a-h-A-M-A")
#     root.set("uid", "demo_test_pc_to_atak")
#     root.set("how", "m-g")
#     root.set("time", pytak.cot_time())
#     root.set("start", pytak.cot_time())
#     root.set(
#         "stale", pytak.cot_time(60)
#     )  # time difference in seconds from 'start' when stale initiates

#     current_phi += (90 / 4)
#     current_phi %= 360

#     new_pos = geod.Direct(loc_center[0], loc_center[1], current_phi, 10)

#     pt_attr = {
#         "lat": f"{new_pos['lat2']:.8f}",  # set your lat (this loc points to Central Park NY)
#         "lon": f"{new_pos['lon2']:.8f}",  # set your long (this loc points to Central Park NY)
#         "hae": "0",
#         "ce": "10",
#         "le": "10",
#     }
    
#     ET.SubElement(root, "point", attrib=pt_attr)

#     return ET.tostring(root)