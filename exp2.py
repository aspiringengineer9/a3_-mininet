
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, OVSController
from mininet.log import setLogLevel


class Exp2Topo(Topo):
    
    """
    Defining the topology

    """

    def build(self):
        
        # Creating three hosts with unique IP and same subnet
      
        h1 = self.addHost("h1", ip="10.0.0.1/24")
        h2 = self.addHost("h2", ip="10.0.0.2/24")
        h3 = self.addHost("h3", ip="10.0.0.3/24")

        # Creating two OVS switches
    
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        # Creating ethernet interfaces
        
        self.addLink(h1, s1)   # --> s1-eth1 (port 1)
        self.addLink(h2, s1)   # --> s1-eth2 (port 2)
        self.addLink(s1, s2)   # --> s1-eth3 (port 3), s2-eth1
        self.addLink(s2, h3)   # --> s2-eth2
        """""
        After building, s1 will have ports:
         in port:1 (h1)
         in port:2 (h2)
         in port:3 (s2)

        """""


def run():
    # Build network from above topology
    topo = Exp2Topo()
    net = Mininet(
        topo=topo,
        controller=OVSController,         
        switch=OVSKernelSwitch,            # Using kernel-based OVS switches
        autoSetMacs=True,                  # assign mac addresses
        autoStaticArp=True,                
    )

    # Starting the network
    net.start()

    h1, h2, h3 = net["h1"], net["h2"], net["h3"]
    s1 = net["s1"]

    # Opening the result file
    with open("result2.txt", "w") as f:


        f.write("Ping h1->h3 BEFORE flows:\n")
        f.write(h1.cmd("ping -c 1 10.0.0.3") + "\n")

        f.write("Ping h2->h3 BEFORE flows:\n")
        f.write(h2.cmd("ping -c 1 10.0.0.3") + "\n")

        
        # Clearing already existing flow table
       
        s1.cmd("ovs-ofctl del-flows s1")

        # installing openflow rules
     
        # dropping all traffic entering s1-eth2 (port 2)
        # This would disable h2 → h3 communication.
        s1.cmd('ovs-ofctl add-flow s1 "in_port=2,actions=drop"')

        # forwarding traffic entering s1-eth1 (port 1) to s1-eth3 (port 3)
        # This would enable h1 → h3 communication.
        s1.cmd('ovs-ofctl add-flow s1 "in_port=1,actions=output:3"')

        # forwarding traffic entering s1-eth3 (port 3) back to s1-eth1 (port 1)
        # This would return traffic from h3 → h1.
        s1.cmd('ovs-ofctl add-flow s1 "in_port=3,actions=output:1"')

        # recording installed flows

        flows = s1.cmd("ovs-ofctl dump-flows s1")
        f.write("\nINSTALLED FLOWS:\n")
        f.write(flows + "\n")


        # Testing connectivity after installing flows
    
        #  h1 to h3 ping should succeed
        #  h2 to h3 should fail
        f.write("Ping h1 to h3 after installing flows:\n")
        f.write(h1.cmd("ping -c 1 10.0.0.3") + "\n")

        f.write("Ping h2 to h3 after installing flows (expecting failure):\n")
        f.write(h2.cmd("ping -c 1 10.0.0.3") + "\n")

    # Stop network
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
