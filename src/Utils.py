import logging
import os

def createLogger(name: str, directory: str, file=True, stream=True) -> logging.Logger:
    os.makedirs(directory, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(directory + name + ".log")
    if stream == False:
        c_handler.setLevel(logging.CRITICAL)
    else:
        c_handler.setLevel(logging.INFO)
    if file == False:
        f_handler.setLevel(logging.ERROR)
    else:
        f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('[%(levelname)s]: %(message)s')
    f_format = logging.Formatter('%(asctime)s: [%(levelname)s]: %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

if __name__ == '__main__':
    pass