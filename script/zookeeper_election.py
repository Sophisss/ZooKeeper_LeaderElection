from kazoo.client import KazooClient
import time
import os
import logging

ZK_HOSTS = "127.0.0.1:2181"
ELECTION_PATH = "/election"

# Configure logging
logging.basicConfig(level=logging.INFO)

class LeaderElection:
    def __init__(self, zk_hosts, election_path):
        """
        Initialize the LeaderElection instance.
        :param zk_hosts: Zookeeper host addresses.
        :param election_path: The Zookeeper path used for leader election.
        """
        self.zk_hosts = zk_hosts
        self.election_path = election_path
        self.zk = KazooClient(hosts=self.zk_hosts)
        self.z_node_path = None
        self.is_leader = False

    def start(self):
        """
        Connect to Zookeeper and start leader election.
        """
        self.zk.start()
        self.zk.ensure_path(self.election_path)
        self.z_node_path = self.zk.create(
            f"{self.election_path}/node_",
            ephemeral=True,
            sequence=True
        )
        logging.info(f"Leader election node created in {self.z_node_path}")
        self.elect_leader()

    def elect_leader(self):
        """
        Determine if the current node is the leader.
        If not, set a watch on the immediate predecessor node.
        """
        # Get and sort all nodes under the election path
        nodes = self.zk.get_children(self.election_path)
        nodes.sort()
        my_node = self.z_node_path.split("/")[-1]

        if my_node == nodes[0]:
            logging.info(f"{my_node} is the leader.")
            self.is_leader = True
        else:
            # Otherwise, watch the node immediately before this one
            predecessor = nodes[nodes.index(my_node) - 1]
            logging.info(f"{my_node} is not the leader, watching {predecessor}.")
            self.watch_node(predecessor)
            self.is_leader = False

    def watch_node(self, predecessor):
        """
        Watch the specified predecessor node. If it disappears, re-elect.
        :param predecessor: The predecessor node to watch.
        """
        path = f"{self.election_path}/{predecessor}"

        # Use DataWatch to monitor the predecessor node
        @self.zk.DataWatch(path)
        def watch(data, stat, event):
            if stat is None:
                logging.info(f"Watched node {predecessor} disappeared. Re-electing...")
                self.elect_leader()

    def run_election(self):
        """
        Run an infinite loop performing either leader or follower tasks.
        """
        try:
            while True:
                if self.is_leader:
                    logging.info(f"Process {os.getpid()} is the leader. Doing leader tasks...")
                else:
                    logging.info(f"Process {os.getpid()} is a follower. Waiting for election...")
                time.sleep(5)
        except KeyboardInterrupt:
            logging.info("Stopping election...")
        finally:
            self.zk.stop()
            logging.info("Zookeeper client stopped.")

if __name__ == "__main__":
    election = LeaderElection(ZK_HOSTS, ELECTION_PATH)
    election.start()
    election.run_election()