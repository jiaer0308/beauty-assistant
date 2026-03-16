#!/usr/bin/env python3
"""
API v1 Main Router

Aggregates all v1 endpoint routers under a single prefix.
Add new feature routers here as the app grows.
"""

from fastapi import APIRouter

from app.api.v1.analysis import router as sca_router

api_router = APIRouter()

# SCA endpoints live at  /api/v1/sca/*
api_router.include_router(sca_router, prefix="/sca", tags=["sca"])
