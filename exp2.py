#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.log import setLogLevel


class Exp2Topo(Topo):
    def build(self):
        h1 = self.addHost("h1", ip="10.0.0.1/24")
        h2 = self.addHost("h2", ip="10.0.0.2/24")
        h3 = self.addHost("h3", ip="10.0.0.3/24")

        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        self.addLink(h1, s1)   # s1-eth1 port 1
        self.addLink(h2, s1)   # s1-eth2 port 2
        self.addLink(s1, s2)   # s1-eth3 port 3
        self.addLink(s2, h3)


def run():
    topo = Exp2Topo()
    net = Mininet(
        topo=topo,
        controller=None,
        switch=OVSKernelSwitch,
        autoSetMacs=True,
        autoStaticArp=True,
    )
    net.start()

    h1, h2, h3 = net["h1"], net["h2"], net["h3"]
    s1 = net["s1"]

    with open("result2.txt", "w") as f:
        f.write("=== Experiment 2: SDN (L2) ===\n\n")

        f.write("Ping h1->h3 BEFORE flows:\n")
        f.write(h1.cmd("ping -c 1 10.0.0.3") + "\n")

        f.write("Ping h2->h3 BEFORE flows:\n")
        f.write(h2.cmd("ping -c 1 10.0.0.3") + "\n")

        # Remove all flows
        s1.cmd("ovs-ofctl del-flows s1")

        # ADD OUR CORRECT FLOWS
        # Drop h2
        s1.cmd('ovs-ofctl add-flow s1 "in_port=2,actions=drop"')

        # Forward h1 -> s2
        s1.cmd('ovs-ofctl add-flow s1 "in_port=1,actions=output:3"')

        # Forward s2 -> h1
        s1.cmd('ovs-ofctl add-flow s1 "in_port=3,actions=output:1"')

        flows = s1.cmd("ovs-ofctl dump-flows s1")
        f.write("\nFlows installed:\n")
        f.write(flows + "\n")

        f.write("Ping h1->h3 AFTER flows:\n")
        f.write(h1.cmd("ping -c 1 10.0.0.3") + "\n")

        f.write("Ping h2->h3 AFTER flows (should fail):\n")
        f.write(h2.cmd("ping -c 1 10.0.0.3") + "\n")

    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
