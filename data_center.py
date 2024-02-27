""" Topology API that emulates a simple data center"""

from mininet.topo import Topo
from mininet.log import setLogLevel

class MyTopo( Topo ):

    def build(self, fan_out):

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
        self.hosts = []

        for index in range(1, fan_out * fan_out * fan_out + 1):
            self.hosts.append(self.addHost("h{}".format(index)))


    def addLinks(self):

        # Link core switch and aggregation switch 
        for switch in self.aggr_switch:
            self.addLink(switch, self.core_switch)

        # Link aggregation switches with edge switches
        edge_switch_index = 0
        for switch in self.aggr_switch:
            for i in range(self.fan_out):
                self.addLink(switch, self.edge_switch[edge_switch_index])
                edge_switch_index += 1

        # Link edge switches with hosts
        host_index = 0
        for switch in self.edge_switch:
            for i in range(self.fan_out):
                self.addLink(switch, self.hosts[host_index])
                host_index += 1

def runExperiment(self):
    # create and test the emulator
    topo = myTopo()
    net = Mininet(topo)
    net.start()
    print("Pinging all nodes")
    net.pingAll()
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    runExperiment()