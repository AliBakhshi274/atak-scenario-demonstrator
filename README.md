### Setup

install ```libffi-dev``` as per pytak installation instructions [https://pytak.readthedocs.io/en/latest/installation/].
Then create a venv and install packages from requirements.txt.

### Running

Just execute demo.py, making sure the host is in the same local network as the atak client.
This sends an update every second to the default broadcast UDP address of ATAK, causing a marker to appear on the map at Kantplatz in Darmstadt and perpetually move in a circle.

### Troubleshooting

Check the ATAK client can be reached by the host.
In default config, the ATAK client should also open unicast TCP ports 4242 and 8087, which should show up as 'open' when executing ```nmap [ATAK client IP]``` on the host.
