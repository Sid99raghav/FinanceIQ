#!/usr/bin/env python3
import uvicorn
from uvicorn.config import LOGGING_CONFIG
import sys
import subprocess

# Importing app here makes the syntax cleaner as it will be picked up by refactors
sys.path.append("site")
from main import app

if __name__ == "__main__":
    argc = len(sys.argv)
    arg_port = 8080
    if argc > 1:
        arg_port = int(sys.argv[1])
    print(f"Starting server on port {arg_port}")

    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"

    # https://stackoverflow.com/questions/69138537/uvicorn-fastapi-python-run-both-http-and-https
    # subprocess.Popen(['/home/https_redirect.py'])  # Add this for http redirection
 
    uvicorn.run("main:app",
            host="0.0.0.0",
            port = arg_port,
            workers=2,
            reload=True,
            log_config=log_config,
            ssl_keyfile="/home/ssl/key.pem",
            ssl_certfile="/home/ssl/cert.pem")
