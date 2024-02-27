""" Topology API that emulates a simple data center"""

from mininet.topo import Topo
from mininet.log import setLogLevel
import sys
from mininet.net import Mininet
from mininet.util import irange, dumpNodeConnections

class MyTopo( Topo ):

    def __init__(self, fan_out):

        # Topology initialization
        Topo.__init__(self)

        self.fan_out = fan_out

        # Core switch initialization
        self.core_switch = self.addSwitch("c1")

        # Aggregate layer switches initialization
        self.aggr_switch = []
        for index in range(1, fan_out + 1):
            self.aggr_switch.append(self.addSwitch("a{}".format(index)))

        # Edge switches initialization
        self.edge_switch = []
        for index in range(1, fan_out * fan_out + 1):
            self.edge_switch.append(self.addSwitch("e{}".format(index)))

        # Hosts initialization
        self.hosts_list = []

        for index in range(1, fan_out * fan_out * fan_out + 1):
            self.hosts_list.append(self.addHost("h{}".format(index), cpu=.5/4))

        self.addLinks()


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
    fan_out = sys.argv[1]
    topo = MyTopo(int(fan_out))
    net = Mininet(topo)
    net.start()
    dumpNodeConnections(net.hosts)
    print("Test network connectivity")
    net.pingAll()
    print("Testing bandwidth between h1 and h2")
    h1, h2 = net.get('h1', 'h2')
    if h1 and h2:
        net.iperf((h1, h2))
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    runExperiment()