#!/usr/bin/env python3.6

# ***********************************
#
#   Chaos Bonobo Agent
#
#   Author: CostisC
#
# *********************************** */

from http.client import HTTPConnection, RemoteDisconnected, CannotSendRequest
import sys, argparse, json, os, atexit
from socket import gethostname
import subprocess, logging, logging.handlers
from time import sleep
import experiments as ex

# GLOBALS
regExperiments = []     # the registered (active) experiments
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description =
        """ Chaos Bonobo Agent
        """,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--port', nargs = '?',
        help = "The server's listening port (default: 4440)",
        default = 4440, const = 4440)
    parser.add_argument('-a', '--address', nargs = '?',
        help = "The server's listening address (default: 127.0.0.1)",
        default = '127.0.0.1', const = '127.0.0.1')
    parser.add_argument('-l', '--logfile', nargs = '?',
        help = "Logs filename (default: bonobo.log)",
        default = 'bonobo.log', const = 'bonobo.log')
    parser.add_argument('-f', '--idfile', nargs = '?',
        help = "A script to dynamically compute this host's ID (default: id_script.sh)",
        default = 'id_script.sh', const = None)
    parser.add_argument('-i', '--id', nargs = '?',
        help = "A static ID for this host. It will override the --idfile option")
    parser.add_argument('-t', '--tolerance', nargs = '?',
        help = """A time tolerance (in minutes) that the system can be in an air-gapped state
(i.e. it cannot talk with the server).
After that time, all registered experiements will be removed (default: 5)""",
        default = 5, const = 5)

    return parser.parse_args()


class Client:
    def __init__(self, address: str, port: int) -> None:
        self.address = address
        self.port = port
        self.connection = None
        self.__header = {"Content-Type": "application/json"}


    def start(self) -> None:
        self.connection = HTTPConnection(self.address, self.port, timeout=5)


    def send(self, URL: str, method: str = 'GET',
             header:object = None, body: str = '') -> tuple:
        """
        HTTP client request/response
        Returns: (http_response_code, http_response_desc, content)
        """
        if header is None:
            header = self.__header

        if not self.connection:
            self.start()

        self.connection.request(method, URL, headers=header, body=body)
        resp = self.connection.getresponse()
        output = (resp.status, resp.reason,  resp.read())
        self.connection.close()
        return output


    def post_text_to_server(self, message: str, level: str = "info") -> bool:
        header = {"Content-Type": "text/plain"}
        if not self.connection:
            self.start()
        endpoint = f"/notify?level={level}"
        res = self.send(endpoint, 'POST', header, message)
        return res[0] == 200


    def terminate(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = None


def checkExperiments(regExperiments: list) -> None:
    '''
    Check if experiments are ready to be triggered
    Remove the completed or faulty ones from the registry
    '''
    exp_to_remove = []
    for exp in regExperiments:
        rc = exp.check()
        if rc in (-1,1):
            exp_to_remove.append(exp)

    for i in exp_to_remove:
        logger.info(f"{i} experiment removed from the registry")
        regExperiments.remove(i)


def get_id(idfile: str) -> str:
    """ Return the host's id, as displayed by the idfile script, or None if error
    """
    rc = None
    try:
        rc = subprocess.check_output(['sh', idfile],
                        stderr=subprocess.STDOUT, timeout=2)
        rc = rc.decode('UTF-8').strip()
    except subprocess.CalledProcessError as err:
        logger.error(f"Failed to compute host's ID: {err.output.decode()}")
    except subprocess.TimeoutExpired:
        logger.error(f"Failed to compute host's ID: Script timed out")
    except Exception as err:
        logger.exception("get_id general Exception Error")
    finally:
        return rc

def compose_url(host, hash):
    param = '' if (hash is None) else f"?hash={hash}"
    return f"/experiments/{host}{param}"

@atexit.register
def clearExperiments():
    global regExperiments
    if regExperiments:
        for exp in regExperiments:
            exp.terminate()
    regExperiments = []


def absolute_path(filename: str) -> str:
    if filename[0] != '/':
        return os.path.join(os.path.dirname(__file__), filename)
    else:
        return filename


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    =========> MAIN <===========
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


arg = parse_args()


logger.setLevel(logging.INFO)
file_handler = logging.handlers.RotatingFileHandler(absolute_path(arg.logfile),
                              maxBytes=5*2**20, backupCount=5)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

idfile = idname = None
tolerance = int(arg.tolerance)
hostname = gethostname()
if arg.id:
    hostname = arg.id
else:
    if arg.idfile is not None:
        idfile = absolute_path(arg.idfile)
        if os.path.exists(idfile):
            idname = get_id(idfile)
            if idname is not None:
                idname += " (dynamic)"
                hostname = None

logger.info(f"Agent started with ID: {idname if idname else hostname}")

client = Client(arg.address, arg.port)

hash = None
bRunNextRequest = True
timestamp_of_inaccess = 0
buffer = []

while True:
    try:
        host = hostname if hostname else get_id(idfile)
        experiment_url = compose_url(host, hash)

        (res_code, res_reason, res) = (200, '', '')
        if bRunNextRequest:
            (res_code, res_reason, res) = client.send(experiment_url)
            # reset any previous inaccessible state
            if timestamp_of_inaccess != 0:
                logger.info("Agent reconnected")
                timestamp_of_inaccess = 0
            # if there is a buffer of previously unsend notify-message, try to send them now
            while len(buffer):
                client.post_text_to_server(buffer.pop(0))



        if len(res):
        # A new description of experiments has arrived
            response = json.loads(res)
            hash = response['hash']
            failures = response['failures']
            logger.info(f"Exeperiments initialized: {failures}")

            # register the experiments
            clearExperiments()
            currTime = ex.utils.epoch_time_ms()
            for expermnt in failures:
                # Dynamically synthesize the experiment objects:
                try:
                    expObj = eval(f"ex.{expermnt.get('type')}")
                except AttributeError:
                    logger.error(f"Unknown experiment type '{expermnt.get('type')}'")
                    continue
                # skip past (i.e. already executed) experiments
                if ex.utils.dt_min(expermnt['start'], currTime) > 0:
                    continue
                options = expermnt.get('options', {})
                if options is None:
                    options = {}
                obj = expObj(hostname = host,
                            logger = logger,
                            start =  expermnt['start'],
                            stop =  expermnt['duration'],
                            remote_logger = client.post_text_to_server,
                            notifyBuffer = buffer,
                            **options)
                regExperiments.append(obj)
                logger.info(f"Registered Experiment: {obj}")

        if res_code == 404 and len(regExperiments) != 0:
            logger.info("The previously registered experiments are now deleted")
            clearExperiments()
            hash = None
        elif res_code not in (200,404):
            logger.warning(res_code, res_reason)

        # check in cycles of 'poll' intervals
        for i in range(10):
            checkExperiments(regExperiments)
            sleep(30)
        bRunNextRequest = True

    except (ConnectionRefusedError, RemoteDisconnected,
            CannotSendRequest, OSError) as err:
        if timestamp_of_inaccess == 0:
            logger.error(f"{err}. I will be trying to restart every 5 min...")
            timestamp_of_inaccess = ex.utils.epoch_time_ms()

        client.terminate()
        bRunNextRequest = False
        # if the agent cannot talk with the server for more than 'tolerance' minutes,
        # remove all registered experiments
        if timestamp_of_inaccess != -1 and \
            ex.utils.dt_min(timestamp_of_inaccess, ex.utils.epoch_time_ms()) > tolerance:
            timestamp_of_inaccess = -1
            logger.warning(f"The agent cannot talk with the server for more than {tolerance} min. \
The registered experiments will be removed.")
            clearExperiments()

    except Exception as err:
        logger.exception("Critical Error")
        sys.exit(1)


# *** end of while-loop ***

