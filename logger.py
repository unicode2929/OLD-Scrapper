import os, logging

LOGGING_DEBUG_FORMAT = '[%(levelname)s] %(name)s -> %(message)s'
LOGGING_PROD_FORMAT = '%(message)s'

STATUS_DONE = '[\u2714]'
STATUS_WARNING = '[*]'
STATUS_CRITICAL = '[!]'
STATUS_JOB_RUNNING = '[.]'

class customLog(logging.Logger):

    def __init__(self, name, level=None):
        if level is None:
            env_level = os.getenv('LOG_LEVEL', 'INFO').upper()
            level = getattr(logging, env_level, logging.INFO)

        super().__init__(name, level)

        handler = logging.StreamHandler()

        if level == logging.DEBUG:
            format = LOGGING_DEBUG_FORMAT
        else:
            format = LOGGING_PROD_FORMAT

        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)

        self.addHandler(handler)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.WARNING):
            super().warning(f"{STATUS_WARNING} {msg}", *args, **kwargs)

    def done(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            super().info(f"{STATUS_DONE} {msg}", *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.CRITICAL):
            super().critical(f"{STATUS_CRITICAL} {msg}", *args, **kwargs)

    def job_running(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            super().info(f"{STATUS_JOB_RUNNING} {msg}", *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            super().debug(f"{msg}", *args, **kwargs)