from transitions import Machine
import time
import random

def splitter(transtions):
   return [{"trigger": trans, "source": trans.split("->")[0], "dest":trans.split("->")[1]} for trans in transtions]


class testMAchine(Machine):

    def __init__(self):
        # States
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
                                "s11->s12",
                                "s7->s2",
                                "s7->s6",
                                "s7->s8",
                                "s7->s13",
                                "s13->s7"])
        Machine.__init__(self, states=states, initial='s0', transitions=transitions)
        
        self.to_s0()
    def on_enter_s0(self):
        time.sleep(1)
        print("Enter on S0")
        if True:
            return self.to_s1()
        
        self.to_s2()
        print("nedfojwnfoijnodifnpid vpjw voiwnorivno")
        
        
    def on_enter_s1(self):
        time.sleep(1)
        print(self.state)
        #self.to_s0()
        
    def on_enter_s2(self):
        time.sleep(1)
        print(self.state)
        #self.to_s1()
        

tstm = testMAchine()

