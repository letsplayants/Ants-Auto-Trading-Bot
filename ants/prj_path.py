import sys
from os.path import dirname
import logging

basePath = dirname(__file__)
exchanges = basePath + '/exchanges'
bithumb = exchanges + '/pybithumb'

sys.path.insert(0, basePath)
sys.path.append(exchanges)
sys.path.append(bithumb)

logger = logging.getLogger(__name__)

logger.info(sys.path)

