#!/usr/bin/env python3
"""
FastAPI Dependencies

Provides shared dependencies for the API layer via FastAPI's
Depends() injection system.
"""

from typing import Annotated

from fastapi import Depends, Request

from app.services.sca_workflow_service import SCAWorkflowService


def get_sca_service(request: Request) -> SCAWorkflowService:
    """
    Retrieve the SCAWorkflowService singleton stored on app.state.

    The service is initialised once during application startup (see main.py
    lifespan) so that the heavy ML models are loaded only once, not per
    request.
    """
    return request.app.state.sca_service


# Convenience type alias for use in endpoint signatures
SCAServiceDep = Annotated[SCAWorkflowService, Depends(get_sca_service)]
