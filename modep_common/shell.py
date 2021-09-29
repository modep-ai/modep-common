import logging
import subprocess

logger = logging.getLogger(__name__)


def run_cmd(cmd):
    """ Run a shell command and print the output as it runs """
    logger.debug('$ %s', cmd)
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True,
                               shell=True)
    return_code = None
    while True:
        output = process.stdout.readline()
        return_code = process.poll()
        if return_code is not None:
            logger.debug('RETURN CODE: %i', return_code)
            logger.debug('RETURN CMD:  %s', cmd)
            for output in process.stdout.readlines():
                logger.debug(output.strip())
            break
        logger.debug(output.strip())
    return return_code
