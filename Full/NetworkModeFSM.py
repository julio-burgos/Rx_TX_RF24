from transitions import Machine
import random
from USBManager import *
from FullModeCTE import *
from NetworkModeFunctions import *
import time
from colors import Color
from colors import lightLED
from RF24 import *
import spidev
import RPi.GPIO as GPIO

# TODO: HACER QUE EL LED BLINKEE


def splitter(transtions):
    return [{"trigger": trans, "source": trans.split("->")[0], "dest":trans.split("->")[1]} for trans in transtions]


class NetworkModeFSM(Machine):

    # States

    def __init__(self, initialState, radio, commLedPins, first):
        states = ["s"+str(i) for i in range(14)]
        transitions = splitter(["s0->s1",
                                "s1->s2",
                                "s2->s3",
                                "s3->s2",
                                "s3->s4",
                                "s3->s5",
                                "s4->s5",
                                "s5->s6",
                                "s5->s8",
                                "s6->s6",
                                "s6->s7",
                                "s8->s9",
                                "s0->s10",
                                "s10->s11",
                                "s12->s7"
                                "s11->s12",
                                "s7->s6",
                                "s7->s2",
                                "s7->s13",
                                "s7->s8",
                                "s13->s7"])
        Machine.__init__(self, states=states, initial='s0',
                         transitions=transitions)
        self.stateFSM = initialState
        self.commLedPins = commLedPins
        self.stateFSM["first_tx"] = first
        self.pipe_master_tx = self.pipe_slave_rx = PIPES[0]
        self.pipe_slave_tx = self.pipe_master_rx = PIPES[1]
        self.radio = radio
        # The FSM begins at state S0
        # First and useUSB is only used for testing by reading form the SD not from USB
        self.to_s0()

    def on_enter_s0(self):
        print("Entering on s0")
        # The node checks whether it has a USB connected or not. If so, it will be the first transmitter
        #self.stateFSM["first_tx"] = is_usb_connected()
        # If and only if it is the first transmitter, it will read the file from the USB and adopt an active role, going to S1
        if self.stateFSM["first_tx"]:
            self.stateFSM["data"] = read_file_usb(NETWORK_FILENAME_INPUT)
            return self.to_s1()
        # If it has not a USB connected, it will adopt a passive role and go to state S1O
        else:
            return self.to_s10()

    def on_enter_s1(self):
        # It creates the token
        # TODO: AQUI PODEMOS ABRIR LAS DOS PIPES DE MASTER!!!
        self.radio.stopListening()
        self.radio.openWritingPipe(self.pipe_master_tx)
        self.radio.openReadingPipe(1, self.pipe_master_rx)
        print("Entering on s1")
        self.stateFSM["token_pl"] = create_token_pl(self.stateFSM["addr"])
        # Since it is the first transmitter, it will indicate itself as the source node of the token (that is, the node that sent
        # the token to it)
        self.stateFSM["src_token"] = self.stateFSM["addr"]
        # Once the token is created, it will go to state S2
        return self.to_s2()

    def on_enter_s2(self):
        lightLED(self.commLedPins, Color.magenta)
        print("Entering on s2")
        # It starts the polling phase and stores lists of the nodes that have replied to it both yes or no
        self.stateFSM["reply_yes"], self.stateFSM["reply_no"] = poll_and_send(
            self.stateFSM["addr"], self.stateFSM["data"], self.radio, self.pipe_master_tx, self.pipe_master_rx)
        # We update the variable pointing that we have tried to poll once more
        self.stateFSM["retransmission"] = self.stateFSM["retransmission"] + 1
        # Once the polling is done, it goes to state S3
        return self.to_s3()

    def on_enter_s3(self):
        # If no node has replied and it has not reached the maximum number of retries to do the polling,
        # it tries again the polling by going backwards to state S2
        print("Entering on S3")
        if len(self.stateFSM["reply_yes"]) == 0 and len(self.stateFSM["reply_no"]) == 0 and self.stateFSM["retransmission"] < MAX_RETRIES_POLL:
            return self.to_s2()
        # If there are any node that has replied yes or no, it will go directly to state S5. Moreover,
        # it will also go to state S5 if the maximum number of retries is reached and no node has answered
        else:
            return self.to_s5()

    # S4 IS NOT NEEDED: THE SENDING OF THE FILES IS DONE IN THE POLLING PHASE

    def on_enter_s5(self):
        # It updates the token and checks if the token is full, which means that all nodes have the data or
        # that all that have the data have also had the token role
        print("Entering on S5")
        self.stateFSM["token_pl"], token_full = update_token(self.stateFSM["addr"],
                                                             self.stateFSM["token_pl"], self.stateFSM["reply_yes"], self.stateFSM["reply_no"])
        # Therefore, if the token is full, the transmission needs to be terminated and it will go to state S8
        if token_full:
            return self.to_s8()
        # If the token is not full, the token needs to be sent to another node that has the data but has not had
        # the token role in order to see whether this node can contact with the remaining nodes that do not have
        # the data yet. Therefore, it will go to state S6
        else:
            return self.to_s6()

    def on_enter_s6(self):
        # The token is sent to another node
        print("Entering on S6")
        token_sent = send_token(self.stateFSM["addr"], self.stateFSM["src_token"],
                                self.stateFSM["token_pl"], self.stateFSM["reply_yes"], self.stateFSM["reply_no"], self.radio, self.pipe_master_tx, self.pipe_master_rx)
        # If, after trying, the node has not succeeded in sending the token (there may be a failure of the system),
        # it goes directly to state S8
        if not token_sent:
            print("Token cant be sended")
            return self.to_s8()
        # Once the token has been sent, the node, that has been the token up to now, adopts a passive role by going
        # to state S7
        else:
            # TODO: CERRAR LAS PIPES DE MASTER Y ABRIR LAS DE SLAVE
            self.radio.stopListening()
            self.radio.closeReadingPipe(1)
            self.radio.openWritingPipe(self.pipe_slave_tx)
            self.radio.openReadingPipe(1, self.pipe_slave_rx)
            print("Token Sended Correctly")
            return self.to_s7()

    def on_enter_s8(self):
        # The node, which knows that all the nodes that were able to receive the data have already received it,
        # sends an EOT in a broadcast manner and goes right after to state S9
        # Before sending the EOT paxcket, in order to prevent collisions from nodes sending EOT in a broadcast
        # manner at the same time, it waits a random backoff of a value between 0 and 1 second.
        # In order that there is a high probability that all nodes receive it, we send the EOT many times
        print("Entering on S8")
        for i in range(EOT_SEND_RETRIES):
            time.sleep(random.random())
            send_EOT(self.stateFSM["addr"], self.radio, self.pipe_master_tx)
        print("Sended EOTs")
        return self.to_s9()

    def on_enter_s9(self):
        # If and only if the node has not been the first node in the transmission chain, it will wait for a USB to
        # be connected and once it is, it will save the data on it in a file
        print("Entering on S9")
        if not self.stateFSM["first_tx"]:
            lightLED(self.commLedPins, Color.cyan)
            wait_til_usb_connected()
            write_file_usb(NETWORK_FILENAME_OUTPUT, NETWORK_FILENAME_OUTPUT)
        # THIS IS THE END OF THE NETWORK MODE
        lightLED(self.commLedPins, Color.green)
        print("Finish fucking NetMode")
        return

    def on_enter_s10(self):
        lightLED(self.commLedPins, Color.red)
        # If the node is not the first transmitter, it adopts a passive role and waits for a hello packet in order
        # it can receive the file
        # TODO: ABRIR LAS 2 PIPES DE SLAVE
        self.radio.stopListening()
        self.radio.openWritingPipe(self.pipe_slave_tx)
        self.radio.openReadingPipe(1, self.pipe_slave_rx)
        print("entering on S10")
        self.stateFSM["polling_addr"] = wait_hello(
            self.stateFSM["addr"], self.radio, self.pipe_slave_rx)
        print("Hello recieved")
        # Once it receives a hello packet, it goes to state S11
        return self.to_s11()

    def on_enter_s11(self):
        # After receiving a Hello packet, it sends a Reply_Yes message to the polling address
        print("Entering on S11")
        send_reply_yes(self.stateFSM["addr"],
                       self.stateFSM["polling_addr"], self.radio, self.pipe_slave_tx)
        # It goes to state S12
        print("Sended reply YES !")
        return self.to_s12()

    def on_enter_s12(self):
        # It receives the file
        print("Entering on S12")
        self.stateFSM["data"], fallen_node = receive_file(
            self.stateFSM["addr"], self.stateFSM["polling_addr"], self.radio, self.pipe_slave_tx, self.pipe_slave_rx)
        # If after sending the Reply Yes, we do not receive or stop receiving data packets,
        # we go again to state S10 to wait for a Hello
        if fallen_node:
            return self.to_s10()
        # After receiving the file, it copies it in local
        copy_file(self.stateFSM["data"], NETWORK_FILENAME_OUTPUT)
        print("File copied in Local")
        # Once it has copied the file, it goes to state S7
        return self.to_s7()

    def on_enter_s7(self):
        lightLED(self.commLedPins, Color.blue)
        # In this state, it waits for a packet and, depending on the received packet, it acts accordingly
        print("Entering on S7")
        src, dest1, is_ack, SN, dest2, packet_type, pl = wait_packet(
            self.stateFSM["addr"], self.radio, self.pipe_slave_rx)
        print("A packet has been received")
        print("Packet Type: "+str(packet_type))

        # Maybe, even though we have correctly received the file, the transmitter has not received well the ACK that
        # we have sent. Therefore, we send the ACK again and do nothing more
        if packet_type == NETWORK_PACKET_TYPE_DATA or packet_type == NETWORK_PACKET_TYPE_EOF:
            send_ack(src, self.stateFSM["addr"],
                     self.radio, self.pipe_slave_tx)
            return self.to_s7()
        elif packet_type == NETWORK_PACKET_TYPE_PASSTOKEN:
            print("Node has received a token")
            # Since it receives a token packet, it acknowledges it
            send_ack(src, self.stateFSM["addr"],
                     self.radio, self.pipe_slave_tx)
            # In order to make sure that the sending node has been correctly notified about the good reception of the token, we wait
            # TIMEOUT_TOKEN in order to wait for any repeated token packet that it sends
            time_first = time.time()
            while True:
                # After receiving a token, we wait for some time to receive more packets in case that the sending node
                # has not been correctly notified that the token has been correctly received
                _, _, _, _, _, packet_type, _, timeout_reached = wait_packet_timeout(
                    self.stateFSM["addr"], self.radio, self.pipe_slave_rx, TIMEOUT_TOKEN)
                # If the timeout has been reached at the radio level, we exit the function
                time_actual = time.time()
                # If it has finally reached a the timeout in the lower layers without receiving any pckets, it can be said
                # that the sending node is aware of the good reception and that is in passive state
                if timeout_reached:
                    break
                # If we have received another tocket on time, we acknowledge it again
                elif packet_type == NETWORK_PACKET_TYPE_PASSTOKEN:
                    send_ack(src, self.stateFSM["addr"],
                             self.radio, self.pipe_slave_tx)
                # If the timeout is reached, again it can be said that the sending node is aware of the good reception of the token
                elif time_actual >= time_first + TIMEOUT_TOKEN:
                    break

             # TODO: PARA ENVIAR EL TOKEN, O PARA SER ACTIVOS SI EL TOKEN ES PARA NOSOTROS, DEBEMOS SER ACTIVOS. CERRAMOS LA PIPE DE SLAVE Y ABRIMOS 2 DE MASTER
            self.radio.stopListening()
            self.radio.closeReadingPipe(1)
            self.radio.openWritingPipe(self.pipe_master_tx)
            self.radio.openReadingPipe(1, self.pipe_master_rx)

            print("ACK has sended to acknowledge the token")
            # If it receives a token packet and it is intended to it, it obtains the payload, stores the address
            # of the node that sent the token to it and goes to state S2
            if dest2 == self.stateFSM["addr"]:
                print("Token is for me")
                self.stateFSM["src_token"] = src
                self.stateFSM["token_pl"] = pl
                return self.to_s2()
            # If it receives a token packet and it is not intended to it, it forwards the token to another node
            else:
                # If possible, send the token directly to one of the reachable nodes (that are the ones listed
                # in the reply_yes and reply_no variables)
                if dest2 in self.stateFSM["reply_yes"] or dest2 in self.stateFSM["reply_no"]:
                    print("Token is one of my neigbours")
                    dest1 = dest2
                # If not, forward the token through the node that sent the token to it
                else:
                    print("Forward the token to the source")
                    dest1 = self.stateFSM["src_token"]
                token_ack_received = False
                time_first = time.time()
                print("Dest1 ", dest1)
                print("Dest2 ", dest2)
                while True:
                    send_network_packet(self.stateFSM["addr"], dest1, PACKET_FIELD_ISACK_NO_ACK, PACKET_FIELD_SN_FIRST, dest2,
                                        NETWORK_PACKET_TYPE_PASSTOKEN, pl, self.radio, self.pipe_master_tx)
                    token_ack_received = wait_token_ack(
                        self.stateFSM["addr"], self.radio, self.pipe_master_rx)
                    time_actual = time.time()
                    if token_ack_received or time_actual >= time_first + TIMEOUT_TOKEN:
                        break

                if not token_ack_received:
                    return self.to_s2()
                else:
                    # If the received token is not directed to it, it stays in the same state S7 after forwarding the token correctly
                    # TODO; SI LO HEMOS ENVIADO BIEN, CERRAMOS LAS PIPES DE MASTER Y ABRIMOS DE SLAVE DE NUEVO
                    self.radio.stopListening()
                    self.radio.closeReadingPipe(1)
                    self.radio.openWritingPipe(self.pipe_slave_tx)
                    self.radio.openReadingPipe(1, self.pipe_slave_rx)
                    return self.to_s7()
        # If it receives a Hello packet, it stores the address of the polling node and goes to the state S13
        elif packet_type == NETWORK_PACKET_TYPE_CONTROL and pl[-1] == NETWORK_PACKET_CONTROL_HELLO_PAYLOAD:
            print("Hello packet received")
            self.stateFSM["polling_addr"] = src
            return self.to_s13()
        # If it receives an EOT packet, it goesd to the state S8
        elif packet_type == NETWORK_PACKET_TYPE_CONTROL and pl[-1] == NETWORK_PACKET_CONTROL_EOT_PAYLOAD:
            print("EOT packet received")
            # TODO: CERRAR LAS PIPES DE SLAVE Y ABRIR UNA WRITING DE MASTER PARA ENVIAR EL EOT
            self.radio.stopListening()
            self.radio.closeReadingPipe(1)
            self.radio.openWritingPipe(self.pipe_slave_tx)
            return self.to_s8()

    def on_enter_s13(self):
        # If the node is in a passive role, has already received the data and receives a Hello packet from a node,
        # it sends a Reply_No to this polling node and goes back to the waiting state S7
        print("Entering on S13")
        send_reply_no(self.stateFSM["addr"],
                      self.stateFSM["polling_addr"], self.radio, self.pipe_slave_tx)
        print("Sended reply NO !!!")
        return self.to_s7()
