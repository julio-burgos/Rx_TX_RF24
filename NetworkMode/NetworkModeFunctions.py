from NetworkModeCTE import *
import time
from RFfunctions import *
from PacketManager import *
from buffer import Buffer
from getPackets import *


def create_token_pl(self_addr):
    print("Creating Token")
    #
    #                                                 TOKEN STRUCTURE
    #
    #    -----------------------------------------------------------------------------------------------------------
    #   |                                                     |                                                     |
    #   |                       DATA FLAG                     |                     TOKEN FLAG                      |
    #   |                                                     |                                                     |
    #    -----------------------------------------------------------------------------------------------------------
    #   |      NODE 1     |      NODE 2     |      NODE 3     |      NODE 1     |      NODE 2     |      NODE 3     |
    #    -----------------------------------------------------------------------------------------------------------
    #   |                 |                 |                 |                 |                 |                 |
    #   | 0 0 0 0 0 0 0 1 | 0 0 0 0 0 0 0 1 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 1 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 |
    #   |                 |                 |                 |                 |                 |                 |
    #    -----------------------------------------------------------------------------------------------------------
    #
    #   The above token payload means that both nodes 1 and 2 have the data but only node 1 has had the token role
    #
    # First of all we create an empty bytearray of size PAYLOAD_SIZE
    token_pl = bytearray(NETWORK_PAYLOAD_SIZE)
    # We have to put to 1 both the bit that indicates that a node has the data and the bit that indicates
    # that a node has been the token
    token_pl[self_addr-1] = 1
    token_pl[self_addr+NETWORK_SIZE-1] = 1

    print("Token : "+str(list(token_pl)))
    return token_pl


def poll_and_send(self_addr, data, radio, pipe_tx, pipe_rx):
    print("Sending Hello")
    reply_yes = []
    reply_no = []
    # Since it will send the packets after one node sends a Reply Yes, we obtain the packets from
    # the data we have (then, we have the payload of the data packets, which will be identical for
    # all the nodes)
    packetsList = getPackets(data, NETWORK_PAYLOAD_SIZE)
    # It starts polling all the nodes except itself
    for addr_to_poll in range(1, NETWORK_SIZE+1):
        if addr_to_poll != self_addr:
            # It sends a Hello packet
            print("Sending hello to " + str(addr_to_poll))
            time_first = time.time()
            reply_received = False
            timeout_reached = False
            while True:
                send_hello(self_addr, addr_to_poll, radio, pipe_tx)
                # Only if the timeout is not reached, it considers the received packet. If the timeout is
                # reached, it goes on with the following node
                reply_received, pl = wait_hello_reply(
                    self_addr, addr_to_poll, radio, pipe_rx)
                # If we have received the reply from the node we were polling, we will exit
                if reply_received:
                    break

                # After having tried many times, if the node does not respond, it is because it is fallen or there is
                # no direct connection with it. Therefore, it goes on with the next node as well
                time_actual = time.time()
                if time_actual >= time_first + TIMEOUT_HELLO:
                    timeout_reached = True
                    break

            # If the timeout has not been reached and it is a control packet, it checks if it is
            # a Reply Yes or a Reply No that comes from the polled node
            if not timeout_reached and reply_received:
                # In case it is a Reply Yes, it adds this node to the Reply Yes list and sends the
                # file to it

                if pl[-1] == NETWORK_PACKET_CONTROL_REPLY_YES_PAYLOAD:
                    reply_yes.append(addr_to_poll)
                    # SEGUIR POR AQUI
                    fallen_node = send_file(
                        self_addr, addr_to_poll, packetsList, radio, pipe_tx, pipe_rx)
                    # If after receiving the Reply Yes, the node sends data packets to it and at some
                    # moment does not receive any ACK after MAX_RETRIES retries, it removes this node
                    # from the Reply Yes list, since the node is not working properly
                    if fallen_node:
                        reply_yes.remove(addr_to_poll)
                # In case it is a Reply No, it adds this node to the Reply No list
                if pl[-1] == NETWORK_PACKET_CONTROL_REPLY_NO_PAYLOAD:
                    reply_no.append(addr_to_poll)
    return reply_yes, reply_no


def update_token(self_addr, token_pl, reply_yes, reply_no):
    # We update the token by saying that the current node has had the token role
    print("Token Before update: "+str(list(token_pl)))
    token_pl[self_addr+NETWORK_SIZE-1] = 1
    # We update the token to indicate that all the nodes that replied yes have now the data.
    if len(reply_yes) != 0:
        for i in range(len(reply_yes)):
            token_pl[reply_yes[i]-1] = 1

    # Furthermore, in case there has been any failure at the end of the transmission of the file
    # before and some of the nodes that had replied no did not appear in the token that they already
    # had the file, we also indicate again that this node has the data as well
    if len(reply_no) != 0:
        for i in range(len(reply_no)):
            token_pl[reply_no[i]-1] = 1

    # We indicate whether the token is full or not
    token_full = False
    # Token full means all nodes have the data or all that have the data have also been token role
    token_full = sum(token_pl[0:NETWORK_SIZE]) == NETWORK_SIZE or sum(
        token_pl[0:NETWORK_SIZE]) == sum(token_pl[NETWORK_SIZE:2*NETWORK_SIZE])

    print("Token After update: "+str(list(token_pl)))
    return token_pl, token_full


def send_token(self_addr, src_token, token_pl, reply_yes, reply_no, radio, pipe_tx, pipe_rx):
    # First of all, based on the token payload (token_pl), we see which are the nodes that, while having the data,
    # have not been the token yet. To do that, we implement an xor, since the nodes that have been the token may necessarily
    # have the data
    # if we are the first node and, we will only be able to sen
    if self_addr != src_token:
        possible_token_candidates = reply_yes + reply_no + \
            [i for i in range(1, NETWORK_SIZE+1)
             if i not in reply_yes and i not in reply_no]
    else:
        possible_token_candidates = reply_yes + reply_no

    print("Possible token candidate: "+str(possible_token_candidates))
    print("Reply YES: "+str(reply_yes))
    print("Reply NO: "+str(reply_no))
    print("Token to send: "+str(list(token_pl)))

    token_candidates = []
    for token_candidate in possible_token_candidates:
        if (token_pl[token_candidate-1] ^ token_pl[token_candidate-1+NETWORK_SIZE]):
            token_candidates.append(token_candidate)

    print("Token candidates: "+str(token_candidates))

    token_ack_received = False
    # If there is a node in the Reply_Yes list that is candidate to be the token, it chooses one of theses nodes
    for token_candidate in token_candidates:
        token_ack_received = False
        # It tries to receive an ack from the chosen node up to a maximum number of MAX_RETRIES retries
        time_first = time.time()
        while True:
            send_network_packet(self_addr, token_candidate, PACKET_FIELD_ISACK_NO_ACK, PACKET_FIELD_SN_FIRST, token_candidate,
                                NETWORK_PACKET_TYPE_PASSTOKEN, token_pl, radio, pipe_tx)
            token_ack_received = wait_token_ack(self_addr, radio, pipe_rx)
            print("Is token ACK received? " + str(token_ack_received))
            time_actual = time.time()
            # If the node does not respond, it goes on  with the following token candidate in the list. On the other hand,
            # if the destination node has sent the token ack, it also stops
            if time_actual >= time_first + TIMEOUT_TOKEN or token_ack_received:
                break
        # It only stops from searching candidates whenever a candidate sends the corresponding acknowledgement for the token
        if token_ack_received:
            break
    return token_ack_received


def send_file(self_addr, dst_addr, packetsList, radio, pipe_tx, pipe_rx):
    print("Sending Data to "+str(dst_addr))
    # First of all, we obtain the number of data packets to be sent
    numPackets = len(packetsList)

    # We define some of the fields that are to be common for all the packets
    src = self_addr
    dest1 = dst_addr
    dest2 = dst_addr
    is_ack = PACKET_FIELD_ISACK_NO_ACK

    # We iterate through all the packets
    for index, packet in enumerate(packetsList):
        # For the sequence number the receiver only needs to check whether this is the desired packet or if it is
        # the same packet than before that has been repeated due to the loss of the ACK
        SN = index % 2
        # The last packet is indicated by the packet type End Of File
        if index == numPackets - 1:
            packet_type = NETWORK_PACKET_TYPE_EOF
        # If it is not the last packet, it is a normal data packet type
        else:
            packet_type = NETWORK_PACKET_TYPE_DATA

        # Sending the data is crucial for the functioning of the system. Therefore, we need an acknowledgement
        data_ack_received = False
        # We define a variable in order to control that the receiving node falls. Therefore, it will avoid to be hang
        # on this transmission

        fallen_node = False
        # Then, it will try to send each packet a MAX_RETRIES number of times. If no ACK is received, it exits the function
        # and tries with the following node if any
        time_first = time.time()
        while True:
            send_network_packet(src, dest1, is_ack, SN, dest2,
                                packet_type, packet.getBufferString(), radio, pipe_tx)
            data_ack_received = wait_data_ack(src, radio, pipe_rx)
            time_actual = time.time()
            if time_actual >= time_first + TIMEOUT_DATA:
                fallen_node = True
                print("Timeout reached on the sending side")
                break
            if fallen_node or data_ack_received:
                break
        # If the node has fallen, we stop trying sending packets to it
        if fallen_node:
            break

    if not fallen_node:
        print("Sended File Correctly to " + str(dst_addr))

    return fallen_node


def send_EOT(self_addr, radio, pipe_tx):
    # We obtain an empty payload of NETWORK_PAYLOAD_SIZE size
    EOT_pl = bytearray(NETWORK_PAYLOAD_SIZE)
    # Since it is a control packet, it will only occupy the last byte
    EOT_pl[-1] = NETWORK_PACKET_CONTROL_EOT_PAYLOAD
    # We send the EOT packet
    send_network_packet(self_addr, NETWORK_BROADCAST_ADDR, PACKET_FIELD_ISACK_NO_ACK, PACKET_FIELD_SN_FIRST, NETWORK_BROADCAST_ADDR,
                        NETWORK_PACKET_TYPE_CONTROL, EOT_pl, radio, pipe_tx)


def wait_hello(self_addr, radio, pipe_rx):
    # It waits for a Hello packet to be received and returns the polling address
    while True:
        src, dest1, is_ack, SN, dest2, packet_type, pl = wait_packet(
            self_addr, radio, pipe_rx)
        if packet_type == NETWORK_PACKET_TYPE_CONTROL and pl[-1] == NETWORK_PACKET_CONTROL_HELLO_PAYLOAD:
            break
    return src


def wait_data_ack(self_addr, radio, pipe_rx):
    # It waits for an ACK packet to be received and returns the polling address
    time_first = time.time()
    src = dest1 = is_ack = SN = dest2 = packet_type = pl = None
    data_ack_received = False
    timeout_reached = False
    while True:
        src, dest1, is_ack, SN, dest2, packet_type, pl, timeout_reached = wait_packet_timeout(
            self_addr, radio, pipe_rx, TIMEOUT_DATA_ACK)
        # If the timeout has been reached at the link level, we exit the function
        if timeout_reached:
            break
        # Maybe before at the link level we have received a packet but it was not
        # an ack packet. Therefore, at network level, we control the timeout as well
        time_actual = time.time()
        if time_actual >= time_first + TIMEOUT_DATA_ACK:
            timeout_reached = True
            break
        if packet_type == NETWORK_PACKET_TYPE_CONTROL and is_ack == PACKET_FIELD_ISACK_YES_ACK:
            data_ack_received = True
            break

    return data_ack_received


def wait_token_ack(self_addr, radio, pipe_rx):
    # It waits for an ACK packet to be received and returns the polling address
    time_first = time.time()
    src = dest1 = is_ack = SN = dest2 = packet_type = pl = None
    token_ack_received = False
    timeout_reached = False
    while True:
        src, dest1, is_ack, SN, dest2, packet_type, pl, timeout_reached = wait_packet_timeout(
            self_addr, radio, pipe_rx, TIMEOUT_TOKEN_ACK)
        # If the timeout has been reached at the link level, we exit the function
        if timeout_reached:
            break
        # Maybe before at the link level we have received a packet but it was not
        # an ack packet. Therefore, at network level, we control the timeout as well
        time_actual = time.time()
        if time_actual >= time_first + TIMEOUT_TOKEN_ACK:
            timeout_reached = True
            break
        if packet_type == NETWORK_PACKET_TYPE_CONTROL and is_ack == PACKET_FIELD_ISACK_YES_ACK:
            token_ack_received = True
            break

    return token_ack_received


def wait_hello_reply(self_addr, addr_to_poll, radio, pipe_rx):
    # It waits for an ACK packet to be received and returns the polling address
    time_first = time.time()
    src = dest1 = is_ack = SN = dest2 = packet_type = pl = None
    reply_received = False
    timeout_reached = False
    while True:
        src, dest1, is_ack, SN, dest2, packet_type, pl, timeout_reached = wait_packet_timeout(
            self_addr, radio, pipe_rx, TIMEOUT_HELLO_REPLY)
        # If the timeout has been reached at the link level, we exit the function
        if timeout_reached:
            break
        # Maybe before at the link level we have received a packet but it was not
        # an ack packet. Therefore, at network level, we control the timeout as well
        time_actual = time.time()
        if time_actual >= time_first + TIMEOUT_HELLO_REPLY:
            timeout_reached = True
            break
        if packet_type == NETWORK_PACKET_TYPE_CONTROL and src == addr_to_poll:
            if pl[-1] == NETWORK_PACKET_CONTROL_REPLY_YES_PAYLOAD or pl[-1] == NETWORK_PACKET_CONTROL_REPLY_NO_PAYLOAD:
                reply_received = True
                break

    return reply_received, pl


def send_ack(src, self_addr, radio, pipe_tx):
    # The src is the source address of the packet that we want to acknowledge. self_addr is our address,
    # the address to which the packet that we want to acknowledge was sent
    # We obtain an empty payload of NETWORK_PAYLOAD_SIZE size
    ack_pl = bytearray(NETWORK_PAYLOAD_SIZE)
    # We send the ACK packet
    send_network_packet(self_addr, src, PACKET_FIELD_ISACK_YES_ACK, PACKET_FIELD_SN_FIRST, src,
                        NETWORK_PACKET_TYPE_CONTROL, ack_pl, radio, pipe_tx)


def send_reply_yes(self_addr, polling_addr, radio, pipe_tx):
    # We obtain an empty payload of NETWORK_PAYLOAD_SIZE size
    reply_yes_pl = bytearray(NETWORK_PAYLOAD_SIZE)
    # Since it is a control packet, it will only occupy the last byte
    reply_yes_pl[-1] = NETWORK_PACKET_CONTROL_REPLY_YES_PAYLOAD
    # We send the Reply_Yes packet
    send_network_packet(self_addr, polling_addr, PACKET_FIELD_ISACK_NO_ACK, PACKET_FIELD_SN_FIRST, polling_addr,
                        NETWORK_PACKET_TYPE_CONTROL, reply_yes_pl, radio, pipe_tx)


def send_reply_no(self_addr, polling_addr, radio, pipe_tx):
    # We obtain an empty payload of NETWORK_PAYLOAD_SIZE size
    reply_no_pl = bytearray(NETWORK_PAYLOAD_SIZE)
    # Since it is a control packet, it will only occupy the last byte
    reply_no_pl[-1] = NETWORK_PACKET_CONTROL_REPLY_NO_PAYLOAD
    # We send the Reply_No packet
    send_network_packet(self_addr, polling_addr, PACKET_FIELD_ISACK_NO_ACK, PACKET_FIELD_SN_FIRST, polling_addr,
                        NETWORK_PACKET_TYPE_CONTROL, reply_no_pl, radio, pipe_tx)


def send_hello(self_addr, addr_to_poll, radio, pipe_tx):
    # We obtain an empty payload of NETWORK_PAYLOAD_SIZE size
    hello_pl = bytearray(NETWORK_PAYLOAD_SIZE)
    # Since it is a control packet, it will only occupy the last byte
    hello_pl[-1] = NETWORK_PACKET_CONTROL_HELLO_PAYLOAD
    # We send the Hello packet
    send_network_packet(self_addr, addr_to_poll, PACKET_FIELD_ISACK_NO_ACK, PACKET_FIELD_SN_FIRST, addr_to_poll,
                        NETWORK_PACKET_TYPE_CONTROL, hello_pl, radio, pipe_tx)


def receive_file(self_addr, polling_addr, radio, pipe_tx, pipe_rx):

    # RECIBIR LA CARPETA. QUIZA EL TRANSMISOR AUN NO HA RECIBIDO EL REPLY_YES Y ME HAYA SEGUIDO ENVIANDO HELLOS.
    # POR ELLO, HAY QUE ESUCHAR SI NOS ENVIA UN PAQUETE DE HELLO PARA VOLVER A DECIRLE REPLY_YES
    data = []
    previous_SN = None
    EOF = False
    fallen_node = False
    datastr = ''
    print("Starting to recive the file in node" + str(self_addr))
    # While the packet is not the last one, indicated by the packet type EOF, it keeps on receiving
    while not EOF:
        time_first = time.time()
        # We wait to receive each packet a maximum of TIMEOUT_DATA time
        while True:
            src, dest1, is_ack, SN, dest2, packet_type, pl, timeout_reached = wait_packet_timeout(
                self_addr, radio, pipe_rx, TIMEOUT_DATA)
            # If the timeout has been reached at lower layers, it exits
            if timeout_reached:
                fallen_node = True
                break
            else:
                # Perhaps, the polling node has not received yet the Reply_Yes packet. Then, it sends again the Reply_Yes
                # and resets the counter of the timeout for this data packet
                if packet_type == NETWORK_PACKET_TYPE_CONTROL and pl[-1] == NETWORK_PACKET_CONTROL_HELLO_PAYLOAD:
                    send_reply_yes(self_addr, polling_addr, radio, pipe_tx)
                    break
                # If it has correctly received a data packet, whether it is the expected one or not, it resets the
                # counter of the timeout for this data packet
                if packet_type == NETWORK_PACKET_TYPE_DATA or packet_type == NETWORK_PACKET_TYPE_EOF:
                    break

            time_actual = time.time()
            if time_actual >= time_first + TIMEOUT_DATA:
                fallen_node = True
                break

        # If the receiving node has been waiting to receive a packet for more than TIMEOUT_DATA time, it exits and goes
        # again to the waiting Hello state
        if fallen_node:
            break

        # If it is a data packet (whether it is EOF or not), it sends an ACK
        if packet_type == NETWORK_PACKET_TYPE_DATA or packet_type == NETWORK_PACKET_TYPE_EOF:

            send_ack(src, self_addr, radio, pipe_tx)

            # Only if the SN is different from the previous one, it considers the packet
            if SN != previous_SN:
                data.append(arrayToString(pl))
                previous_SN = SN
            # If it is EOF, it stops from receiving the data
            if packet_type == NETWORK_PACKET_TYPE_EOF:
                EOF = True
                print("EOF received")

    if not fallen_node:
        datastr = ''.join(data)
        print("File correctly received "+str(self_addr))

    return datastr, fallen_node


def wait_packet(self_addr, radio, pipe_rx):
    # We wait until we receive a packet that is intended to us at L2, that is, when self_addr == dest1,
    # or until we receive a broadcast packet
    while True:
        packet = wait_radio_packet(radio, pipe_rx)
        src, dest1, is_ack, SN, dest2, packet_type, pl = decode_packet(packet)
        if dest1 == self_addr or dest1 == NETWORK_BROADCAST_ADDR:
            break

    return src, dest1, is_ack, SN, dest2, packet_type, pl


def wait_packet_timeout(self_addr, radio, pipe_rx, timeout):
    # We wait until we receive a packet that is intended to us at L2, that is, when self_addr == dest1 if and
    # only if we receive before the timeout
    time_first = time.time()
    src = dest1 = is_ack = SN = dest2 = packet_type = pl = None
    timeout_reached = False
    while True:
        packet, timeout_reached = wait_radio_packet_timeout(
            radio, pipe_rx, timeout)

        # If the timeout has been reached at the radio level, we exit the function
        # Maybe before at the radio level we have received a packet but it was not
        # intended for us. Therefore, at link level, we control the timeout as well
        time_actual = time.time()
        if time_actual >= time_first + timeout or timeout_reached:
            timeout_reached = True
            break
        # Therefore, if we have received on time a packet, we see whether it is intended for

        # us or not
        src, dest1, is_ack, SN, dest2, packet_type, pl = decode_packet(packet)
        # If the packet is intended for us or it is the EOT broadcast packet, we exit the function
        if dest1 == self_addr or dest1 == NETWORK_BROADCAST_ADDR:
            break

    return src, dest1, is_ack, SN, dest2, packet_type, pl, timeout_reached


def send_network_packet(src, dest1, is_ack, SN, dest2, packet_type, pl, radio, pipe_tx):
    # We create the packet following the Network packet structure
    packet = create_packet(src, dest1, is_ack, SN, dest2, packet_type, pl)

    # We send the packet through the radio interface
    send_radio_packet(packet, radio, pipe_tx)
