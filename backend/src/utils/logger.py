import os
import logging

class CustomLogger:
    """Custom logger wrapper for AWS Lambda execution environments."""

    def __init__(self, name: str = "monitus"):
        self.logger = logging.getLogger(name)
        
        # Configure log level from environment variable (default: INFO)
        log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        self.logger.setLevel(log_level)

        # Avoid adding multiple handlers during Lambda container warm starts
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(levelname)s]\t%(asctime)s.%(msecs)03dZ\t[%(name)s]\t%(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # Prevent duplicate logs from bubbling up to the Lambda root logger
            self.logger.propagate = False

    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """Logs error message along with full Python exception stack trace."""
        self.logger.exception(message, *args, **kwargs)


def get_logger(module_name: str) -> CustomLogger:
    """Factory helper to return a named CustomLogger instance."""
    return CustomLogger(module_name)