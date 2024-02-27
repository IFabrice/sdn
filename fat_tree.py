""" Topology API that emulates a simple data center"""

from mininet.topo import Topo
from mininet.log import setLogLevel
import sys
from mininet.net import Mininet
from mininet.util import irange, dumpNodeConnections

class MyTopo( Topo ):

    def __init__(self, k):

        # Topology initialization
        Topo.__init__(self, params={'sopts': {'private_ip'}})

        self.k = k

        self.addSwitch("c1", {'private_ip': "10.0.0.2"})

        self.addHost("h1")
        self.addHost("h2")
        self.addLink('c1', 'h1')
        self.addLink('c1', 'h2')
        

    def addLinks(self):

        # Link core switch and aggregation switch 
        for switch in self.aggr_switch:
            self.addLink(switch, self.core_switch, bw=10, delay='5ms', loss=1, max_queue_size=1000, use_htb=True)

        # Link aggregation switches with edge switches
        edge_switch_index = 0
        for switch in self.aggr_switch:
            for i in range(self.fan_out):
                self.addLink(switch, self.edge_switch[edge_switch_index], bw=10, delay='5ms', loss=1, max_queue_size=1000, use_htb=True)
                edge_switch_index += 1

        # Link edge switches with hosts
        host_index = 0
        for switch in self.edge_switch:
            for i in range(self.fan_out):
                self.addLink(switch, self.hosts_list[host_index], bw=10, delay='5ms', loss=1, max_queue_size=1000, use_htb=True)
                host_index += 1

def runExperiment():
    # create and test the emulator
    topo = MyTopo()
    net = Mininet(topo)
    net.start()
    net.pingAll()
    print("Testing bandwidth between h1 and h2")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    runExperiment()