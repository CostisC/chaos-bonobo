## List of Experiment Types  
The list below explains the different types of supported experiments, with their respective settings.  
The implementation and instructions for these experiments are incorporated in the Agents.  
If new failures are wished to be included in your experiments, the Agents can be expanded, according to the [Developer Guide](developerGuide.md).  


### Block_Address  
Add a firewall rule to block incoming/outgoing traffic from/to the specified source/destination.  
Duration instruction: Required  

**Options**  
*policy*: Possible values: INPUT, OUTPUT  
*ip*:  The IP address to block. A source address in the INPUT policy case, or a destination address in the OUTPUT policy case.  
*protocol*: The protocol (e.g. tcp, udp) when referencing a port  
*sport*: Block packages with this source port   
*dport*: Block packages with this destination port

**Example**  
```
type: Block_Address
  options:
    policy: INPUT
    ip: 10.10.140.100
```

### Traffic_Throttling
Impose delays, jitter or packet loss to the egress traffic of a network interface.  
Delay and jitter cannot be applied together with packet loss, at the same time.  
Duration instruction: Required  

**Options**  
*device*: The network interface device (e.g. eth0)  
*delay*: Milliseconds of delay  
*jitter*: Milliseconds of jitter. It should always be set together with *delay*  
*packet_loss*: Percentage of lost packets   


**Example**  
```
type: Traffic_Throttling
  options:
    device: eth0
    delay: 200
    jitter: 100
```

### Kill_Process
Send a specific signal (SIGKILL, by default) to the running process(es), matching a name.  
Duration instruction: N/A

**Options**  
*pname*: The name of running process(es) to match. It will match the output of *pidof* command.   
*signal*: The signal to send to the matched process(es). It can be either the signal's full name or its numeric representation.  Default: SIGKILL(9)

**Example**  
```
type: Kill_Process
  options:
    pname: mongod
    signal: SIGTERM
```


### Stop_Service
Stop a systemd service, for a specified period.  
Duration instruction: Required  

**Options**  
*service*: The name of the running service to stop.  

**Example**  
```
type: Stop_Service
  options:
    service: sshd
```

### Spawn_Command
Spawn a process, which should be run as a detached daemon.  
Duration instruction: Required  

**Options**  
*command*: The command line

**Example**  
```
type: Spawn_Command
  options:
    command: 'sleep 200'
```

### Reboot
Reboot the system  
Duration instruction: N/A 

**Options**  
N/A

**Example**  
```
type: Reboot
```


### Kernel_Panic
Cause a Kernel Panic  
Duration instruction: N/A 

**Options**  
N/A

**Example**  
```
type: Kernel_Panic
```
