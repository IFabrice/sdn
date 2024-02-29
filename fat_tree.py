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
        for index in range(1, ((k * k) // 4) + 1):

            # i represent rows and j represent columns
            i = index // (k//2)
            j = index % (k//2)

            # creating dpid in the form "00 : 00 : 00 : 00 : 00 : k : j : i"
            dpid = "00:00:00:00:00:" + str(k) + ":"+ str(i) + str(j)

            self.core_switches.append(self.addSwitch('c{}'.format(index), dpid=dpid))

        
        for pod in range(0, k):
            
            init_index = len(self.edge_switches)

            # initialization of aggregate and edge switches
            for index in range(0, k//2):

                # initialization of pid of the form "00 : 00 : 00 : 00 : 00 : pod : switch : 01"
                aggr_dpid = "00:00:00:00:00:" + str(pod) + ":" + str(index + k//2) + ":" + "01"
                self.aggr_switches.append(self.addSwitch('a{}'.format(index + pod*k//2), dpid=aggr_dpid))

                edge_dpid = "00:00:00:00:00:" + str(pod) + ":" + str(index) + ":" + "01"
                self.edge_switches.append(self.addSwitch("e{}".format(index + pod*k//2), dpid=edge_dpid))

                self.addEdgeHosts(pod, index)
            
            self.addAggr_EdgeLinks(init_index)
        
        # self.addCore_AggrLinks()

    
    def addCore_AggrLinks(self):

        # Add links for core and aggregate switches
        for core_index in range(len(self.core_switches)):
            for pod in range(self.k):
                in_pod_index = (core_index) // (self.k//2)
                aggr_index = pod * self.k//2 + in_pod_index
                self.addLink(self.core_switches[core_index], self.aggr_switches[aggr_index], port1=pod, port2=self.k//2 + pod + core_index)


    def addAggr_EdgeLinks(self, index):
        
        # connect each aggregate switches to corresponding edge switches
        edge_port = self.k//2
        for aggr_switch in self.aggr_switches[index:]:
            aggr_port = 0
            for edge_switch in self.edge_switches[index:]:
                self.addLink(aggr_switch, edge_switch, port1=aggr_port, port2=edge_port)
                aggr_port += 1
            
            edge_port += 1


        # for aggr_index in range(index, index + self.k//2):
        #     for edge_index in range(index, index + self.k//2):
        #         self.addLink(self.aggr_switches[aggr_index], self.edge_switches[edge_index], port1=aggr_index - index, port2=edge_index - index + self.k)



        
    def addEdgeHosts(self, pod, switch):
        
        # initialize k hosts and link all of them to the current edge switch. Note: hosts ip is in format: "10.pod.switch.ID"
        for index in range(self.k//2):
            ip = "10.{}.{}.{}".format(pod, switch, index + 2)
            host_index = len(self.all_hosts)
            self.all_hosts.append(self.addHost("h{}".format(host_index), ip=ip))

            # connect edge and host with their respective port numbers
            self.addLink(self.edge_switches[-1], self.all_hosts[-1], port1=index, port2=0)




    # def addLinks(self):

    #     # Link core switch and aggregation switch 
    #     for switch in self.aggr_switch:
    #         self.addLink(switch, self.core_switch, bw=10, delay='5ms', loss=1, max_queue_size=1000, use_htb=True)

    #     # Link aggregation switches with edge switches
    #     edge_switch_index = 0
    #     for switch in self.aggr_switch:
    #         for i in range(self.fan_out):
    #             self.addLink(switch, self.edge_switch[edge_switch_index], bw=10, delay='5ms', loss=1, max_queue_size=1000, use_htb=True)
    #             edge_switch_index += 1

    #     # Link edge switches with hosts
    #     host_index = 0
    #     for switch in self.edge_switch:
    #         for i in range(self.fan_out):
    #             self.addLink(switch, self.hosts_list[host_index], bw=10, delay='5ms', loss=1, max_queue_size=1000, use_htb=True)
    #             host_index += 1

def runExperiment():
    # create and test the emulator
    k = sys.argv[1]
    topo = MyTopo(int(k))
    net = Mininet(topo)
    net.start()
    net.pingAll()
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    runExperiment()