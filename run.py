import subprocess
import yaml

# Load YAML config
with open("docker_run_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Build the docker run command
cmd = [
    "docker", "run", "--rm", "-it",
    "--name", config.get("container_name", "mycontainer")
]

# Add volumes
for vol in config.get("volumes", []):
    cmd += ["-v", vol]

# Add ports
for port in config.get("ports", []):
    cmd += ["-p", port]

# Add environment variables
for key, value in config.get("environment", {}).items():
    cmd += ["-e", f'{key}="{value}"']

# Add image
cmd.append(config["image"])

# Add command to execute inside container
if "command" in config:
    cmd += ["bash", "-c", f'{config["command"]}']

# Print and run the command
print("Running:", " ".join(cmd))
subprocess.run(cmd)