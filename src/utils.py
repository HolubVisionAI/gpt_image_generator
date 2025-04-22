import os
import yaml
import logging
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))

log = colorlog.getLogger("colored_logger")
log.addHandler(handler)
log.setLevel(logging.DEBUG)


def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        log.warning(f"Config file not found: {config_path}")
        log.info("Creating a blank config.yaml file...")
        default_yaml = """# Example 
root_paths:
  - parent path of language directory

"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(default_yaml)
        log.warning("Created config.yaml. Please edit it and re-run the script.")
        exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
