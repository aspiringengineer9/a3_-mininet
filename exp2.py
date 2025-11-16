#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.log import setLogLevel
import re


class Exp2Topo(Topo):
    def build(self):
        h1 = self.addHost("h1", ip="10.0.0.1/24")
        h2 = self.addHost("h2", ip="10.0.0.2/24")
        h3 = self.addHost("h3", ip="10.0.0.3/24")

        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(s1, s2)
        self.addLink(s2, h3)


def get_port_mapping(switch):
    output = switch.cmd("ovs-ofctl show s1")
    lines = output.split("\n")
    mapping = {}
    for line in lines:
        m = re.match(r"\s*(\d+)\(([^)]+)\)", line)
        if m:
            port_num = m.group(1)
            port_name = m.group(2)
            mapping[port_name] = port_num
    return mapping


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

    # Detect real switch port numbers
    ports = get_port_mapping(s1)

    p_h1 = [ports[p] for p in ports if "h1" in p][0]
    p_h2 = [ports[p] for p in ports if "h2" in p][0]
    p_s2 = [ports[p] for p in ports if "s2" in p][0]

    with open("result2.txt", "w") as f:
        f.write("=== Experiment 2: SDN (L2) ===\n\n")

        f.write("Ping h1->h3 BEFORE flows:\n")
        f.write(h1.cmd("ping -c 1 10.0.0.3") + "\n")

        f.write("Ping h2->h3 BEFORE flows:\n")
        f.write(h2.cmd("ping -c 1 10.0.0.3") + "\n")

        # Clear flows and add new ones
        s1.cmd("ovs-ofctl del-flows s1")

        s1.cmd(f'ovs-ofctl add-flow s1 "in_port={p_h2},actions=drop"')
        s1.cmd(f'ovs-ofctl add-flow s1 "in_port={p_h1},actions=output:{p_s2}"')
        s1.cmd(f'ovs-ofctl add-flow s1 "in_port={p_s2},actions=output:{p_h1}"')

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
