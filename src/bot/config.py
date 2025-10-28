import os, yaml
from typing import Any, Dict

def _merge(a, b):
    for k, v in b.items():
        if isinstance(v, dict) and k in a:
            _merge(a[k], v)
        else:
            a[k] = v

def load_config(path: str, overrides_path: str|None=None) -> Dict[str,Any]:
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    if overrides_path and os.path.exists(overrides_path):
        with open(overrides_path, "r") as f:
            over = yaml.safe_load(f)
        _merge(cfg, over)
    # env expansion for simple ${VAR}
    def expand(x):
        if isinstance(x, str) and x.startswith("${") and x.endswith("}"):
            return os.getenv(x[2:-1], "")
        if isinstance(x, dict):
            return {k:expand(v) for k,v in x.items()}
        if isinstance(x, list):
            return [expand(i) for i in x]
        return x
    return expand(cfg)
