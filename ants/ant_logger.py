import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
logger.addHandler(stream_hander)

file_handler = logging.FileHandler('./logs/ants.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

