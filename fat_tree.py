""" Topology API that emulates a simple data center"""

from mininet.topo import Topo
from mininet.log import setLogLevel
import sys
from mininet.net import Mininet
from mininet.util import irange, dumpNodeConnections



class MyTopo( Topo ):

    def __init__(self, k, **opts):

        # Topology initialization
        Topo.__init__(self, **opts)
        
        self.k = k
        self.core_switches = []
        self.aggr_switches = []
        self.edge_switches = []
        self.all_hosts = []

        # initialize core switches
        for index in range(1, pow(k/2, 2) + 1):

            # i represent rows and j represent columns
            i = index / (k/2)
            j = index % (k/2)

            # creating dpid in the form "00 : 00 : 00 : 00 : 00 : k : j : i"
            dpid = "00:00:00:00:00:" + str(k) + ":"+ str(i) + str(j)

            self.core_switches.append(self.addSwitch('c{}'.format(index), dpid))

        
        for pod in range(0, k):
            
            # initialization of aggregate and edge switches
            for index in range(0, k/2):

                # initialization of pid of the form "00 : 00 : 00 : 00 : 00 : pod : switch : 01"
                aggr_dpid = "00:00:00:00:00:" + str(pod) + ":" + str(index + k/2) + ":" + "01"
                self.aggr_switches.append(self.addSwitch('a{}'.format(index + pod*k/2), aggr_dpid))

                edge_dpid = "00:00:00:00:00:" + str(pod) + ":" + str(index) + ":" + "01"
                self.edge_switches.append(self.addSwitch("e{}".format(index + pod*k/2), edge_dpid))

                self.addEdgeHosts(pod, index)


        
    def addEdgeHosts(self, pod, switch):
        
        # initialize k hosts and link all of them to the current edge switch. Note: hosts ip is in format: "10.pod.switch.ID"
        for index in range(self.k):
            ip = "10.{}.{}.{}".format(pod, switch, index)
            self.all_hosts.append(self.addHost("c{}".format(index), ip=ip))
            self.addLink(self.edge_switches[-1], self.all_hosts[-1])




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
    c1 = net.get("c1")
    print("The private IP for c1 is {}".format(c1.private_ip))

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    runExperiment()