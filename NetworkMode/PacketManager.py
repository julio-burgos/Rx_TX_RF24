from NetworkModeCTE import *
from RFfunctions import *


def create_header(src, dest1, is_ack, SN, dest2, packet_type):
    # We obtain the link layer header
    L2Header = src << 4 | dest1
    # We obtain the network layer header
    L3Header = (int(is_ack) << 7) | (SN << 6) | (dest2 << 2) | packet_type
    return [L2Header, L3Header]


def create_packet(src, dest1, is_ack, SN, dest2, packet_type, pl):
    # We obtain the header
    header = create_header(src, dest1, is_ack, SN, dest2, packet_type)
    # We create an empty packet
    packet = bytearray(PACKET_LENGTH)
    # In such packet, we include the obtained header at the beginning
    packet[0:NETWORK_HEADER_SIZE] = header
    # Following the header, we include the given payload
    packet[NETWORK_HEADER_SIZE:] = pl
    return packet


def read_header(header):
    # We obtain the L2 source address
    src = header[0] >> 4
    # We obtain the L2 destination address
    dest1 = header[0] & 15
    # We obtain if it is an ACK packet
    is_ack = header[1] >> 7
    # We obtain the sequence number
    SN = (header[1] >> 6) & 1
    # We obtain the L3 destination address
    dest2 = (header[1] >> 2) & 15
    # We obtain the packet type
    packet_type = header[1] & 3
    return src, dest1, is_ack, SN, dest2, packet_type


def decode_packet(packet):
    # We obtain all the fields of the header
    src, dest1, is_ack, SN, dest2, packet_type = read_header(
        packet[0:NETWORK_HEADER_SIZE])
    # We obtain the payload of the packet
    pl = packet[NETWORK_HEADER_SIZE:]
    return src, dest1, is_ack, SN, dest2, packet_type, pl
