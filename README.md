## Chaos Bonobo  
Chaos Bonobo is a framework for implementing and scheduling the injection of failures and disruptions in the normal operation of hosts.  
It consists of two types of components. One central Server and multiple Agents.
The Server should run on a separate host, and it is where the user will schedule which experiments should be executed on which targeted hosts, when to be triggered and for how long.  

![Components](Documentation/docs/img/components.png)


### Build the components
> Note: In order to advance the release number of the produced next deliverables, update the `Version` file before building the components.

There are three make targets that will generate the following delivarbles:
- **build_agent**: Produce an RPM package which will install the Agent 
- **build_docs**: Generate Documentation pages, to be included in a new release of a Server package. 
It should be executed, if there are any changes in the Documentation content.
- **build_server**: Produce an RPM package which will install the Server

The default target is to produce all deliverables. Simply:  
```
make 
```


### Install the Server
Chaos Bonobo Server is implemented on Node.js. Therefore, Node.js should be already installed in the host where the Server will be installed.  
Then proceed with installing the Server, from its package:
```
rpm -ivh chaos-bonobo-server-x.y-z.rpm
```

Next, start the server:
```
systemctl start chaos-bonobo-server
```

The Server includes the latest Documentation of the framework.  
Simply browse to `http://<chaos-bonobo_server_ip>:4440/docs` and continue from there.  
