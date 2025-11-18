
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info


class Linux_router(Node):
    """
    Let's enable IPv4 forwarding inside router node. now, r1 and r2 can forward packets between interfaces.
    
    """
    def config(self, **params):
        super(Linux_router, self).config(**params)
        # Enable packet forwarding 
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        # disable packet forwarding when router shuts down
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(Linux_router, self).terminate()


class Exp1Topo(Topo):
    """
    Let's define the topology given; This would create links between hosts and routers according to the given topology diagram
   
    """

    def build(self):
        # creating hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        # Creating router nodes
        r1 = self.addNode('r1', cls=Linux_router)
        r2 = self.addNode('r2', cls=Linux_router)

        # Creating links between routers and hosts
        self.addLink(h1, r1)   
        self.addLink(r1, r2)   
        self.addLink(r2, h3)   
        self.addLink(h2, r1)   


def run():
    # Building topology and starting the network functions
    topo = Exp1Topo()
    net = Mininet(topo=topo, controller=None)
    net.start()

    
    h1, h2, h3 = net['h1'], net['h2'], net['h3']
    r1, r2 = net['r1'], net['r2']

    
    # Assigning IP addresses to all interfaces
    
    h1.setIP('10.0.0.1/24', intf='h1-eth0')
    r1.setIP('10.0.0.3/24', intf='r1-eth0')

    r1.setIP('10.0.1.1/24', intf='r1-eth1')
    r2.setIP('10.0.1.2/24', intf='r2-eth0')

    r2.setIP('10.0.2.1/24', intf='r2-eth1')
    h3.setIP('10.0.2.2/24', intf='h3-eth0')

    r1.setIP('10.0.3.4/24', intf='r1-eth2')
    h2.setIP('10.0.3.2/24', intf='h2-eth0')

    
    # Set default gateways for the hosts (h1, h2, h3)
    
   
    h1.cmd('ip route del default || true')
    h1.cmd('ip route add default via 10.0.0.3')   # sends traffic to router r1

    h2.cmd('ip route del default || true')
    h2.cmd('ip route add default via 10.0.3.4')   # sends traffic to router r1

    h3.cmd('ip route del default || true')
    h3.cmd('ip route add default via 10.0.2.1')   # sends traffic to router r2

   
    # writing static routes for routers
    # Routers would hence know how to reach networks that are not directly connected

    r1.cmd('ip route add 10.0.2.0/24 via 10.0.1.2')

    r2.cmd('ip route add 10.0.0.0/24 via 10.0.1.1')
    r2.cmd('ip route add 10.0.3.0/24 via 10.0.1.1')

   
    # Running all the ping tests and logging results into the file : result1.txt
 
    with open('result1.txt', 'w') as f:
        f.write('Experiment 1: IP Routing\n\n')

        f.write('Ping from h1 (10.0.0.1) to h3 (10.0.2.2)\n')
        f.write(h1.cmd('ping -c 1 10.0.2.2') + '\n')

        f.write('Ping from h2 (10.0.3.2) to h3 (10.0.2.2)\n')
        f.write(h2.cmd('ping -c 1 10.0.2.2') + '\n')

        f.write('Ping from h3 (10.0.2.2) to h1 (10.0.0.1)\n')
        f.write(h3.cmd('ping -c 1 10.0.0.1') + '\n')

        f.write('Ping from h3 (10.0.2.2) to h2 (10.0.3.2)\n')
        f.write(h3.cmd('ping -c 1 10.0.3.2') + '\n')

    # Let's stop the network
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
