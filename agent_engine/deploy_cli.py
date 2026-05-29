"""Deploy the agent to Vertex AI Agent Engine via the ADK CLI."""

import argparse
import json
import logging
import os
import subprocess
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-engine-deployer")

AGENT_SOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent")


def deploy_agent_engine(project: str, region: str, display_name: str) -> None:
    """Run `adk deploy agent_engine` from the agent package directory."""
    if not os.path.isdir(AGENT_SOURCE_DIR):
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": f"Directory {AGENT_SOURCE_DIR} not found",
                }
            )
        )
        sys.exit(1)

    logger.info("Deploying agent %s", display_name)
    logger.info("Source directory: %s", AGENT_SOURCE_DIR)

    command = [
        "adk",
        "deploy",
        "agent_engine",
        f"--project={project}",
        f"--region={region}",
        f"--display_name={display_name}",
        ".",
    ]

    try:
        subprocess.run(
            command,
            cwd=AGENT_SOURCE_DIR,
            capture_output=False,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(
            json.dumps(
                {
                    "status": "error",
                    "stderr": e.stderr,
                    "stdout": e.stdout,
                }
            )
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy agent via ADK CLI")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--region", required=True, help="Agent Engine region")
    parser.add_argument(
        "--display-name",
        required=True,
        help="Display name for the agent in the console",
    )
    args = parser.parse_args()
    deploy_agent_engine(args.project, args.region, args.display_name)


if __name__ == "__main__":
    main()
