import antsworker as worker
import logging

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)

    file_handler = logging.FileHandler('./logs/ants.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("Ant start working...")

    worker.init()
    worker.start()
    