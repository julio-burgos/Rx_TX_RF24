from NetworkModeFSM import NetworkModeFSM
from RFfunctions import config_radio
from NetworkModeCTE import *
import sys

radio = config_radio(channel=NETWORK_CHANNEL,
                     power=NETWORK_PA_LEVEL, rate=NETWORK_DATARATE)

state = {"addr": NETWORK_SELF_ADDR, "first_tx": False, "token_pl": [], "reply_yes": [], "reply_no": [],
         "retransmission": 0, "data": [], "src_token": None, "polling_addr": None}
first = False
if len(sys.argv) == 3:
    state["addr"] = int(sys.argv[1])
    first = sys.argv[2] == 'True'

networkfsm = NetworkModeFSM(state,
                            radio,
                            useUSB=False, first=first
                            )
