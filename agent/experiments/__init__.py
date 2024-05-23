from . import utils
from .BaseClass import BaseExperiment

class Block_Address(BaseExperiment):

    def start(self) -> bool:
        policy = self.options.get('policy')
        ip_switch = ''
        if policy == 'INPUT':
            ip_switch = 's'
        elif policy == 'OUTPUT':
            ip_switch = 'd'
        else:
            self.notify(f"Unsupported policy {policy}")
            return False

        ip_address = self.options.get('ip')
        if ip_address:
            ip_address = f"-{ip_switch} {ip_address}"
        else:
            ip_address = ''

        sport = self.options.get('sport')
        if sport:
            sport = f"--sport {sport}"
        else:
            sport = ''
        dport = self.options.get('dport')
        if dport:
            dport = f"--dport {dport}"
        else:
            dport = ''

        protocol = self.options.get('protocol')
        if protocol is None:
            if sport != '' or dport != '':
                self.notify("No protocol defined for port blocking")
                return False
            else:
                protocol = ''
        else:
            protocol = f"-p {protocol}"

        signature = '_'.join([ str(i) for i in self.options.values() ])

        command = f"iptables -I {policy} 1 {ip_address} {protocol} {sport} {dport} -j DROP \
        -m comment --comment 'BLOCK_{signature}'"

        return super().start(command)

    def terminate(self):
        policy = self.options.get('policy')

        signature = '_'.join([ str(i) for i in self.options.values() ])

        command = f"iptables -L  {policy} -n --line-numbers |\
        grep BLOCK_{signature} | awk '{{print $1}}' | xargs  iptables -D {policy}"

        return super().terminate(command)



class Kill_Process(BaseExperiment):

    def start(self) -> bool:
        pname = self.options.get('pname', 'UNDEFINED')
        signal = self.options.get('signal', 'SIGKILL')
        flag = '-' if str(signal).isnumeric() else '-s '

        command = f"/usr/bin/kill {flag}{signal} $(pidof {pname})"

        return super().start(command)


class Traffic_Throttling(BaseExperiment):

    def start(self) -> bool:
        device = self.options.get('device')
        delay = self.options.get('delay')
        jitter = self.options.get('jitter')
        if jitter and delay is None:
            self.notify("Cannot set jitter without delay")
            return False
        packet_loss = self.options.get('packet_loss')

        if delay:
            jttr = f"{jitter}ms" if jitter else ''
            command = f"tc qdisc add dev {device} root netem delay {delay}ms {jttr}"
        else:
            command = f"tc qdisc add dev {device} root netem loss {packet_loss}%"

        return super().start(command)


    def terminate(self) -> bool:
        device = self.options.get('device')
        command = f"tc qdisc del dev {device} root"

        return super().terminate(command)



class Stop_Service(BaseExperiment):

    def start(self) -> bool:
        service_name = self.options.get('service')
        command = f"systemctl stop {service_name}"
        return super().start(command)

    def terminate(self) -> bool:
        service_name = self.options.get('service')
        command = f"systemctl start {service_name}"
        return super().terminate(command)


class Spawn_Command(BaseExperiment):

    def start(self) -> bool:
        command = self.options.get('command')
        return super().start(command, detached = True)


class Reboot(BaseExperiment):
    def start(self) -> bool:
        command = "reboot"
        return super().start(command)


class Kernel_Panic(BaseExperiment):
    def start(self) -> bool:
        command = "sync; echo c > /proc/sysrq-trigger"
        return super().start(command)
