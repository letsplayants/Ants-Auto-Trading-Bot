import ant_logger
import prj_path
import ant_tele
import antsworker as worker
import logging

if __name__ == '__main__':
    logger=logging.getLogger(__name__)
    
    logger.info("Ant start working...")

    worker.init()
    worker.start()
    