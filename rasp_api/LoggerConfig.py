import logging
import sys


consoleHandler = logging.StreamHandler(stream=sys.stdout)
filelogHandler = logging.FileHandler(filename="../files/debug.log")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [%(levelname)s] | %(module)s Func: %(funcName)s() Line: %(lineno)d| %(message)s",
    datefmt='%Y-%d-%m / %H:%M:%S',
    handlers=[consoleHandler, filelogHandler]
)
