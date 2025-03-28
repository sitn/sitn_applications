#!/usr/bin/env python3
import argparse
import subprocess
import os
from datetime import datetime
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

ALLOWED_INSTANCES = ["prepub", "prod", "dev", "local"]

def check_settings_file(dest_instance):
    # Do not deploy to the internet with DEBUG set to True
    settings_file = Path("./ppe_numerique/settings.py")
    with open(settings_file, 'r') as f:
        settings = f.read()
    is_debug = bool(re.search(r"^\s*DEBUG\s*=\s*True\s*$", settings, re.MULTILINE))
    if is_debug and dest_instance not in ["local", "dev"]:
        sys.exit("Cannot deploy if DEBUG=True in settings.py")

def main():
    parser = argparse.ArgumentParser(description="Déploiement PPE numérique")
    parser.add_argument("env", nargs="*", help="The environment config")
    args = parser.parse_args()
    if len(args.env) != 1:
        sys.exit("Vous devez utiliser ce script avec un argument: prepub|prod|local|dev")

    instance = args.env[0]

    if instance not in ALLOWED_INSTANCES:
        sys.exit("Le premier argument est faux.")

    check_settings_file(instance)

    env_file = f".env.{instance}"
    os.environ['ENV_FILE'] = env_file
    load_dotenv(Path(env_file), override=True)

    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - DOCKER_HOST is: {os.environ['DOCKER_HOST']}")

    cmd = ["docker-compose", "build"]
    print(" ".join(cmd))
    subprocess.check_call(cmd)

    cmd = ["docker-compose", "down", "-v"]
    print(" ".join(cmd))
    subprocess.check_call(cmd)

    cmd = ["docker-compose", "up", "-d"]
    print(" ".join(cmd))
    subprocess.check_call(cmd)
    os.environ["DOCKER_HOST"] = ""
    
    print("\a")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - END")

if __name__ == "__main__":
    main()
