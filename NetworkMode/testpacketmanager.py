from NetworkModeCTE import *
from PacketManager import *


src = 2
dest1 = 3
is_ack = PACKET_FIELD_ISACK_NO_ACK
SN = PACKET_FIELD_SN_FIRST
dest2 = 7
packet_type = NETWORK_PACKET_TYPE_CONTROL
pl = bytearray(NETWORK_PAYLOAD_SIZE)
pl[-1] = NETWORK_PACKET_CONTROL_REPLY_YES_PAYLOAD

packet = create_packet(src, dest1, is_ack, SN, dest2, packet_type, pl)
src_rx, dest1_rx, is_ack_rx, SN_rx, dest2_rx, packet_type_rx, pl_rx = decode_packet(
    packet)

print(src_rx, dest1_rx, is_ack_rx, SN_rx, dest2_rx, packet_type_rx, pl_rx)

print(NETWORK_PACKET_CONTROL_REPLY_YES_PAYLOAD == pl[-1])
