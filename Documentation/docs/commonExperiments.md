## Experiments description

The full set of experiments is centrally defined on the Server, in a file of a YAML syntax.  
Its default location is `/etc/chaos-bonobo/experiments.yaml` (also ref. [Server Configuration](installation.md#server-configuration)).

Its layout can be examined with an example, as follows:
```
- host: 10.10.10.10
  failures:
    - type: Block_Address
      options:
        policy: INPUT
        ip: 10.10.140.100
      #disable: true 
      start:  20:32:30
      duration: 30m

    - type: Kill_Process
      options:
        pname: sshd
        #signal: SIGKILL
      #disable: true 
      start: 0m
      duration: 0m

    - type: Stop_Service
      options:
        service: nfsserver
      #disable: true 
      start: 2023-12-31 23:45
      duration: 45m
        
- host: NTP-server
  failures:
    - type: Block_Address
      options:
        policy: INPUT
        ip: 10.10.140.100
      #disable: true 
      start: 1h
      duration: 5m
```

### Common experiment settings

We will explain the structure and common settings of the experiments.  
The details of each particular type of experiment are provided in ['Experiments by type'](typeExperiments.md).  

**host**  
The ID by which an Agent, hosted in a targeted machine, identifies itself.  
An Agent that advertises itself with that ID will retrieve the experiments of the matched 'host' list.  
It can be, for instance, the targeted host's IP address (e.g. 10.10.10.10) or its hostname (e.g. NTP-server).  
Also refer to [Dynamic host IDs](installation.md#dynamic-host-ids).  

**failures**  
The set of experiments planned for the corresponding host.  

**type**  
The type of experiment (ref. [Experiments by type](typeExperiments.md)).  

**options**  
The experiment's options, specific to that particular type of experiment (ref. [Experiments by type](typeExperiments.md)).  

**disable**  
If True, this experiment will be skipped. Default value is False.  

**start**  
The trigger time for that experiment.  
It can be either an absolute time/date value, or a relative one,  
with reference to the experiments initiation instance (ref. [Server reload](installation.md#start-the-server)).  

Below are some examples of possible start values.  

Value              | Interpretation
-----------------  | --------------
10:30              | today, at 10:30
2023-10-01 10:30   | on 1st Oct. 2023, at 10:30
2023:10:1  10:30   | as above
2023 10 01 10:30   | as above
2023:10:01         | on 1st Oct. 2023, at 00:00
1h30m              | in 1 hour and 30 minutes from now
13m                | in 13 minutes from now 



**duration**  
How long that experiment/failure should last.  
This is relevant only for experiment types where restoration (i.e. termination) instructions are defined. 
Its accepted syntax is similar to the *start* setting.  
It can be either an absolute point in time, or a duration, in the minutes and hours notation 
(e.g. '5m' will let the failure run for 5 minutes, etc.).  
If left unspecified, the experiment will last 30 seconds.


