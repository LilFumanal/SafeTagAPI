import logging

class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def get_logger(self):
        return self.logger