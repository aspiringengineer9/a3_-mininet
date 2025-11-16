#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.log import setLogLevel, info


class Exp2Topo(Topo):
    """
    L2 topology:

        h1 ---- s1 ---- s2 ---- h3
                |
               h2

    h1-eth0 <-> s1-eth1
    h2-eth0 <-> s1-eth2
    s1-eth3 <-> s2-eth1
    s2-eth2 <-> h3-eth0
    """

    def build(self, **_opts):
        # Hosts on same subnet
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')

        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Links
        self.addLink(h1, s1)   # h1-eth0 <-> s1-eth1
        self.addLink(h2, s1)   # h2-eth0 <-> s1-eth2
        self.addLink(s1, s2)   # s1-eth3 <-> s2-eth1
        self.addLink(s2, h3)   # s2-eth2 <-> h3-eth0


def run():
    topo = Exp2Topo()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        controller=None,       # no external controller
        autoSetMacs=True,
        autoStaticArp=True,
    )
    net.start()

    h1, h2, h3 = net['h1'], net['h2'], net['h3']
    s1 = net['s1']

    info('*** Running automated Experiment 2 and writing result2.txt\n')

    with open('result2.txt', 'w') as f:
        f.write('=== Experiment 2: SDN / L2 ===\n\n')

        # ------------------------------------------------------------
        # Baseline pings (no manual flows yet)
        # ------------------------------------------------------------
        f.write('Baseline ping (no manual flows yet)\n\n')

        f.write('Ping from h1 to h3:\n')
        f.write(h1.cmd('ping -c 1 10.0.0.3'))
        f.write('\n')

        f.write('Ping from h2 to h3:\n')
        f.write(h2.cmd('ping -c 1 10.0.0.3'))
        f.write('\n')

        # ------------------------------------------------------------
        # OpenFlow configuration via ovs-ofctl
        # ------------------------------------------------------------
        f.write('=== OpenFlow configuration ===\n\n')

        # Show initial ports/flows
        show_out = s1.cmd('ovs-ofctl show s1')
        dump_before = s1.cmd('ovs-ofctl dump-flows s1')

        f.write('Command: ovs-ofctl show s1\n')
        f.write(show_out + '\n')

        f.write('Command: ovs-ofctl dump-flows s1 (before adding flows)\n')
        f.write(dump_before + '\n')

        # Clear existing flows and install our own
        s1.cmd('ovs-ofctl del-flows s1')

        # Use *port names* so we don't care what numeric port IDs are.
        # Drop everything coming from h2 (s1-eth2)
        s1.cmd('ovs-ofctl add-flow s1 "in_port=s1-eth2,actions=drop"')

        # Forward traffic from h1 (s1-eth1) to s2 (s1-eth3)
        s1.cmd('ovs-ofctl add-flow s1 "in_port=s1-eth1,actions=output:s1-eth3"')

        # Forward traffic from s2 (s1-eth3) back to h1 (s1-eth1)
        s1.cmd('ovs-ofctl add-flow s1 "in_port=s1-eth3,actions=output:s1-eth1"')

        dump_after = s1.cmd('ovs-ofctl dump-flows s1')

        f.write('Commands used to add flows:\n')
        f.write('ovs-ofctl del-flows s1\n')
        f.write('ovs-ofctl add-flow s1 "in_port=s1-eth2,actions=drop"\n')
        f.write('ovs-ofctl add-flow s1 "in_port=s1-eth1,actions=output:s1-eth3"\n')
        f.write('ovs-ofctl add-flow s1 "in_port=s1-eth3,actions=output:s1-eth1"\n\n')

        f.write('Command: ovs-ofctl dump-flows s1 (after adding flows)\n')
        f.write(dump_after + '\n')

        # ------------------------------------------------------------
        # Pings *after* adding flows
        # ------------------------------------------------------------
        f.write('=== After adding flows ===\n\n')

        f.write('Ping from h1 to h3 after flows:\n')
        f.write(h1.cmd('ping -c 1 10.0.0.3'))
        f.write('\n')

        f.write('Ping from h2 to h3 after flows:\n')
        f.write(h2.cmd('ping -c 1 10.0.0.3'))
        f.write('\n')

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
