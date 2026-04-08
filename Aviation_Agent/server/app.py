# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
FastAPI application for the Aviation Agent Environment.

This module creates an HTTP server that exposes the AviationAgentEnvironment
over HTTP and WebSocket endpoints, compatible with EnvClient.

"""

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:  # pragma: no cover
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e

try:
    from models import AviationAgentAction, AviationAgentObservation
    from server.Aviation_Agent_environment import AviationAgentEnvironment
except ModuleNotFoundError:
    # Fallback for different import contexts
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from models import AviationAgentAction, AviationAgentObservation
    from server.Aviation_Agent_environment import AviationAgentEnvironment


# Create the app with web interface and README integration
app = create_app(
    AviationAgentEnvironment,
    AviationAgentAction,
    AviationAgentObservation,
    env_name="Aviation_Agent",
    max_concurrent_envs=1,  # this value defines the number of concurrent sessions. It can be changed as per requirement.
)


def main(host: str = "0.0.0.0", port: int = 8000):
    
    # Entry point for direct execution via uv run or python -m.

    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(host=args.host, port=args.port)
