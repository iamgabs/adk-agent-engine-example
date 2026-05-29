"""Deploy the ADK agent to Vertex AI Agent Engine."""

import argparse
import logging
import os
from pathlib import Path

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from agent.agent import root_agent

logger = logging.getLogger(__name__)

_DEFAULT_WHL = (
    Path(__file__).resolve().parent.parent / "dist" / "agent_engine-0.1.0-py3-none-any.whl"
)
AGENT_WHL_FILE = os.environ.get("AGENT_WHL_FILE", str(_DEFAULT_WHL))


def create(env_vars: dict[str, str] | None = None) -> None:
    """Creates and deploys the agent."""
    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    if not os.path.exists(AGENT_WHL_FILE):
        logger.error("Agent wheel file not found at: %s", AGENT_WHL_FILE)
        raise FileNotFoundError(f"Agent wheel file not found: {AGENT_WHL_FILE}")

    logger.info("Using agent wheel file: %s", AGENT_WHL_FILE)

    remote_agent = agent_engines.create(
        adk_app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]>=1.88",
            "google-adk",
            AGENT_WHL_FILE,
        ],
        extra_packages=[AGENT_WHL_FILE],
        env_vars=env_vars or {},
    )
    logger.info("Created remote agent: %s", remote_agent.resource_name)
    print(f"\nSuccessfully created agent: {remote_agent.resource_name}")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Deploy ADK agent to Agent Engine")
    parser.add_argument(
        "--project",
        default=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        help="GCP project ID (or set GOOGLE_CLOUD_PROJECT)",
    )
    parser.add_argument(
        "--location",
        default=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
        help="GCP region (or set GOOGLE_CLOUD_LOCATION)",
    )
    parser.add_argument(
        "--staging-bucket",
        default=os.environ.get("STAGING_BUCKET"),
        help="GCS staging bucket, e.g. gs://my-bucket (or set STAGING_BUCKET)",
    )
    args = parser.parse_args()

    if not args.project:
        parser.error("--project or GOOGLE_CLOUD_PROJECT is required")
    if not args.staging_bucket:
        parser.error("--staging-bucket or STAGING_BUCKET is required")

    vertexai.init(
        project=args.project,
        location=args.location,
        staging_bucket=args.staging_bucket,
    )
    create()


if __name__ == "__main__":
    main()
