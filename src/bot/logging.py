import logging, sys

def get_logger(level: str="INFO"):
    log = logging.getLogger("perppatrol")
    if not log.handlers:
        h = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        h.setFormatter(fmt)
        log.addHandler(h)
    log.setLevel(level.upper())
    return log
