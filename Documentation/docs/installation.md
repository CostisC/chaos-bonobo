## Install the Server
On the system that will host the Server, run:

    rpm -ivh chaos-bonobo-server-x.y-z.rpm

### Server Configuration

By default, the Server will be listening on port :4440 and will load the description of experiments from file `/etc/chaos-bonobo/experiments.yaml`.  
If however the default values should be overriden, this can be done though `/etc/chaos-bonobo/server.conf`:

```
PORT=4440
EXPERIMENT_FILE=/etc/chaos-bonobo/experiments.yaml
```

Next, the experiments should be set (ref. [How to set the experiments](commonExperiments.md))

### Start the Server

To start the Server, run:

    systemctl start chaos-bonobo-server

If there are changes in the experiments, or simply their relative trigger or duration times should be re-evaluated, the Server will have to be reloaded:

    systemctl reload chaos-bonobo-server

To stop the Server:

    systemctl stop chaos-bonobo-server


>> *Note: If the Server stays down for more than a pre-defined duration (ref. [TOLERANCE](installation.md#agent-configuration) setting) the Agents will cancel their scheduled experiments.*

<br/>
<br/>
<hr>

## Install the Agents
On each targeted system, install the Agent with the following command:

    rpm -ivh chaos-bonobo-agent-x.y-z.rpm


### Agent Configuration

Set the Agent's configuration in file `/etc/chaos-bonobo/agent.conf`:

```
# The server's listening port 
PORT=4440

# The server's listening address 
ADDRESS=127.0.0.1

# A script to dynamically compute this host's ID 
IDFILE=/etc/chaos-bonobo/id_script.sh

# A static ID for this host. It will override the IDFILE option
#ID=

# Logs filename (default: bonobo.log)
LOGFILE=/var/log/chaos-bonobo-agent/bonobo.log

# A time tolerance (in minutes) that the system can be in an air-gapped state (i.e. it cannot talk with the server).
# After that time, all registered experiements will be removed 
TOLERANCE=5
```

### Dynamic host IDs
A host identifies itself with an ID (ref. Common experiment's [host](commonExperiments.md#common-experiment-settings) field). This is also how it advertises itself to the Server. 
This ID can be either static or dynamic. For instance, in the case of a cluster of hosts, where one node has a distinguished or elevated role 
(e.g. being the master or active node) the dynamic ID can be used, so that the node can identify its having that special role.  
The Agent will compute its dynamic ID, before each communication with the Server.  
The dynamic ID should be the output of the *"IDFILE"* script.  
>> *Note: If the IDFILE script fails, with a return code other than 0, the host's ID will default to its hostname*


<br/>
**Example of a collocated cluster**  
As an example, suppose a collocated cluster of two nodes, in an active/passive resilience mode, where at any given time the active node 
acquires a single virtual IP address (VIP) - i.e. alias or secondary address.  
For example, on the active node of such a cluster, the assigned IP addresses would be as follows 
- provided that the VIP (10.5.42.62 in this example) is plumbed on the 'eth0' network card interface:
```
 # ip a show dev eth0
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 00:50:56:94:4e:61 brd ff:ff:ff:ff:ff:ff
    altname enp2s0
    altname ens32
    inet 10.5.42.60/27 brd 10.5.42.63 scope global eth0
       valid_lft forever preferred_lft forever
    inet 10.5.42.62/27 scope global secondary eth0
       valid_lft forever preferred_lft forever
    inet6 fd00:10:5:42::27/123 scope global
       valid_lft forever preferred_lft forever
    inet6 fd00:10:5:42::25/123 scope global
       valid_lft forever preferred_lft forever
    inet6 fe80::250:56ff:fe94:4e61/64 scope link
       valid_lft forever preferred_lft forever
```

In this example, the active node could identify its role by verifying that the cluster's VIP is assigned to it. 
The VIP could be used as the dynamic ID by which the active node advertises itself to the Server, as such.  
The IDFILE could be as follows:  
```
ifname=eth0
ip a show dev $ifname | awk '
        /secondary/ {
                if (match($0, /inet? (.*)\//, a)) {
                        print a[1]
                        exit 0
                }
                else exit 1
        }
'
```

<br/>
### Start the Agent 

To start the Agent, run:

    systemctl start chaos-bonobo-agent

To stop the Server:

    systemctl stop chaos-bonobo-agent

In order to maintain that the Agents start up at every system boot up, it is advised that you also activate them:

    systemctl enable chaos-bonobo-agent
