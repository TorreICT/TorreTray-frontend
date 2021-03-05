from loggerpy import *
from parameters import *

logger = Logger()
logger.configure(print_level=Level.DEBUG,
          save_level=Level.DEBUG,
          path=WORKING_DIR_PATH + "GUI/",
          info=True)
