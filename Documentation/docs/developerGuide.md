## Add new experiments
Chaos Bonobo is intented to be easily expandable with new experiment sets, according to the particular needs.  
The instructions for how an experiment is implemented reside in the active Agents, 
in the `experiments/__init__.py` file.   

The new type of experiment should be defined as a class which inherits from the `BaseExperiment` parent class.  
The specifics of the implementation details are abstructed in the parent class.  
The developer of the new type should only provide (override) the `start()` and, optionally, the `terminate()` methods.  
The type-specific options will be passed in the instantiation of that class. 

The new experiment should be invoked in the [experiments description](commonExperiments.md) by its 'type:' field, 
which *should exactly match* the name of the class.  

We will demonstrate these operations with constructing the (already provided) [Stop_Service](typeExperiments.md#stop_service), as an example.  


<br/>
### Example

Suppose we wish to add anew an experiment for momentarily stopping a systemd service (e.g. sshd.service).  
The only parameter needed in calling that experiment would be the service's name. E.g. options.service.  
We choose to name this type of experiments as 'Stop_Service'.  
Therefore, its description would be like:
```
type: Stop_Service
   options:
     service: sshd
```

In `experiments/__init__.py` we will add the definition of this new class, named 'Stop_Service'.  
We need to only override the inherited `start()` and `terminate()` methods:  
```
class Stop_Service(BaseExperiment):

    def start(self) -> bool:
        return super().start(command)


    def terminate(self) -> bool:
        return super().terminate(command)
```

The logic of each method should be composed by building the 'command' string, which is the shell commands to be called by the methods.  
The passed options (options.service, in this example) can be retrieved as the class's data member, the 'options' dictionary.  
The complete implementation of `Stop_Service()` will be as follows:  
```
class Stop_Service(BaseExperiment):

    def start(self) -> bool:
        service_name = self.options.get('service')
        command = f"systemctl stop {service_name}"
        return super().start(command)


    def terminate(self) -> bool:
        service_name = self.options.get('service')
        command = f"systemctl start {service_name}"
        return super().terminate(command)
```
