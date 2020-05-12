# -*- encoding: utf-8 -*-

import logging
import sys


logging.basicConfig(stream=sys.stderr, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
