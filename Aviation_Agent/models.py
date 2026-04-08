# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Aviation Agent Environment.

The Aviation_Agent environment simulates Air Traffic Control (ATC) radio communication.
Agents must respond correctly to ATC instructions with proper aviation phraseology.
"""

from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class AviationAgentAction(Action):
    # Action for the Aviation Agent environment - pilot radio response to ATC

    message: str = Field(..., description="Pilot's radio response to ATC instruction")


class AviationAgentObservation(Observation):
    # Observation from the Aviation Agent environment - ATC instruction and feedback

    atc_instruction: str = Field(default="", description="The ATC instruction given to the pilot")
    task_description: str = Field(default="", description="Description of what the pilot should do")
    step_count: int = Field(default=0, description="Number of steps taken in this episode")
