
from subprocess import Popen, PIPE, TimeoutExpired
from typing import Any
from . import utils

class BaseExperiment:
    def __init__(self, hostname,
                       logger,
                       start=None,
                       stop=None,
                       remote_logger=print,
                       notifyBuffer=None,
                       **kwargs):
        self._hostname = hostname
        self._logger = logger
        self._rlogger = remote_logger
        self._buffer = notifyBuffer
        self.options = kwargs
        self._stdout = ''
        self._stderr= ''
        self._process = None
        self._detached = False

        self._start = start if (start is not None) else utils.epoch_time_ms()
        self._stop = stop if (stop is not None) else start
        self._running = False

    def __repr__(self) -> str:
        options = f"options:{self.options}, " if (len(self.options)) else ''
        stop = f" - {utils.epoch2human(self._stop)}" if (self._stop != self._start) else ''
        duration = f"{utils.epoch2human(self._start)}{stop}"
        return f"{self.__class__.__name__} ({options}{duration})"

    def notify(self, str: str, level: str = 'info') -> None:
        className = self.__class__.__name__
        self._logger.info(f"{className}: {str}")
        try:
            if self._rlogger is not None:
                report = f"{self._hostname} - {className}: {str}"
                self._rlogger(report, level)
        except Exception as err:
            self._logger.error(f"Failed to send notify: {err}")
            # add to buffer for sending at a later time
            self._buffer.append(f"[original timestamp: {utils.current_time()}] {report}")



    def _exec(self, command: str) -> bool:
        self._process = Popen(command, shell=True, stdout = PIPE, stderr = PIPE)
        try:
            if not self._detached:
                self._stdout, self._stderr = self._process.communicate(timeout=10)
                if self._process.returncode:
                    self.notify(f"Command Error ({self._process.returncode}) - CMD: {command!r} \
STDOUT: {self._stdout.decode('UTF-8')!r} STDERR: {self._stderr.decode('UTF-8')!r}", 'error' )
                    return False

        except TimeoutExpired:
            self._process.kill()
            self._stdout, self._stderr = self._process.communicate()
            self.notify(f"Command Timeout - CMD: {command!r} \
STDOUT: {self._stdout.decode('UTF-8')!r} STDERR: {self._stderr.decode('UTF-8')!r}", 'error' )
            return False

        return True

    def check(self) -> int:
        """
        Check for the triggering and stopping of an experiment
        Returns:
             0: Successful initiation/state
             1: Successful completion of the experiment
            -1: An Error has occurred
        """
        if not self._running:
            # start time has occurred in the past 1'
            if 1 == utils.dt_min(self._start, utils.epoch_time_ms()):
                    if self.start():
                        return 0
                    else:
                        return -1
        else:
            # termination time has occurred in the past 5'
            if 1 <= utils.dt_min(self._stop, utils.epoch_time_ms()) <= 6:
                    if self.terminate():
                        return 1
                    else:
                        return -1
        return 0


    def start(self, command: str = None, detached: bool = False) -> bool:
        if self._running:
            return True
        self.notify("Experiment started")
        self._detached = detached
        self._running = self._exec(command)
        return self._running

    def terminate(self, command: str = None) -> bool:
        if self._running:
            if self._detached:
                self.notify("Detached process was terminated")
                self._process.terminate()
                self._process.wait()
                return True
            else:
                if command:
                    self.notify("Triggered Experiment was terminated")
                    return self._exec(command)
                else:
                    return True
        return False


