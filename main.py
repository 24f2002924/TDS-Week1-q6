from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Layers, low -> high precedence
DEFAULTS = {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "default-secret-000"}
YAML_DEV = {"debug": True, "api_key": "key-wtre1blqlq"}          # config.development.yaml
DOTENV = {"NUM_WORKERS": "2"}                                      # .env
OS_ENV = {"APP_PORT": "8422", "APP_LOG_LEVEL": "info"}             # OS env vars

ALIASES = {"num_workers": "workers"}


def norm_key(k: str) -> str:
    k = k.strip().lower()
    if k.startswith("app_"):
        k = k[4:]
    return ALIASES.get(k, k)


def coerce(key: str, val):
    if key in ("port", "workers"):
        try:
            return int(str(val).strip())
        except ValueError:
            return val
    if key == "debug":
        if isinstance(val, bool):
            return val
        return str(val).strip().lower() in ("true", "1", "yes", "on")
    return val if isinstance(val, str) else str(val)


def build(overrides: list[str]) -> dict:
    cfg = dict(DEFAULTS)
    for layer in (YAML_DEV, DOTENV, OS_ENV):
        for k, v in layer.items():
            cfg[norm_key(k)] = coerce(norm_key(k), v)
    for item in overrides:
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        k = norm_key(k)
        cfg[k] = coerce(k, v)
    cfg = {k: coerce(k, v) for k, v in cfg.items()}
    cfg["api_key"] = "****"
    return cfg


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    return build(set)
