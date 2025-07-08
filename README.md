# ZooKeeper Leader Election
A simple distributed system that implements a **leader election algorithm** using [Apache ZooKeeper](https://zookeeper.apache.org/) and [Kazoo](https://kazoo.readthedocs.io/) in Python.

This project demonstrates how processes can coordinate automatically to elect a leader and handle failover using **ephemeral sequential znodes** and **watchers**.

> 📄 The full technical report is available [here](./Distributed_Systems.pdf)

## Technologies
| Tool             | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| Apache ZooKeeper | Distributed coordination service with consistency guarantees |
| Python 3.8+      | Implementation language                                      |
| Kazoo            | Python high-level ZooKeeper client                           |
| Docker           | Containerization platform for ZooKeeper server               |
| Python Logging   | For detailed event tracing and debugging                     |


## Quick Setup

### 1. Clone the repository
```bash
git clone https://github.com/Sophisss/ZooKeeper_LeaderElection.git
cd ZooKeeper_LeaderElection
```

### 2. Start ZooKeeper server using Docker
```bash
docker run -d --name zookeeper -p 2181:2181 zookeeper
```

ZooKeeper will be running at `127.0.0.1:2181`.

### 3. Install dependencies
Install the required Python packages using the provided `requirements.txt` file:
```bash
pip install -r requirements.txt
```

## Leader Election Algorithm Description
This project simulates a distributed environment where multiple processes compete to become the leader using ZooKeeper.

The logic is based on ZooKeeper's ephemeral sequential znodes and the watch mechanism. Here is how it works:

1. Each process connects to the ZooKeeper server.
2. It creates an **ephemeral sequential znode** under the path `/election`.
   - Example: `/election/node_0000000003`
3. ZooKeeper automatically assigns a sequence number to each node.
4. All znodes in `/election` are listed and sorted by sequence number.
5. The process whose znode has the **lowest number** becomes the **leader**.
6. Other processes become **followers** and set a **watch** on the znode immediately before theirs.
8. If the watched znode is deleted (the predecessor crashes or disconnects), the follower is notified and re-evaluates its position.
9. The next in line becomes the new leader.

> This simple algorithm guarantees that at any time, there is exactly one leader, and a new one can be elected without restarting the system.


## Running the Application
To simulate a distributed system, open **multiple terminal windows** and run the application in each one.
```bash
python zookeeper_election.py
```

Each instance will:
- Connect to the ZooKeeper server.
- Create its own ephemeral sequential znode.
- Determine if it's the leader or a follower.
- Monitors predecessor znodes and reacts to failures by participating in re-election.

## License
This project is licensed under the **MIT License**.
