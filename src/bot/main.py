from .config import load_config
from .logging import get_logger

def bootstrap(config_path: str, overrides_path: str|None=None):
    cfg = load_config(config_path, overrides_path)
    log = get_logger(cfg["run"]["log_level"])
    return cfg, log
