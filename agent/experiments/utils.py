import time, math

def epoch_time_ms() -> int:
    """
    Get current epoch time, in milliseconds
    """
    return int(time.time() * 1e3)


def dt_min(epoch_1: int, epoch_2: int) -> int:
    """
    Minutes between epoch_2 - epoch_1
    """
    return math.ceil((epoch_2 - epoch_1)/60e3)


def current_time() -> str:
    """
    Get current time in human readable format
    """
    return time.strftime("%H:%M:%S", time.localtime())


def epoch2human(epch: int) -> str:
    """
    Convert epoch time (in milliseconds) to human readable
    """
    return time.strftime("%H:%M", time.localtime(epch/1000))
