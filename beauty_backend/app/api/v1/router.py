#!/usr/bin/env python3
"""
API v1 Main Router

Aggregates all v1 endpoint routers under a single prefix.
Add new feature routers here as the app grows.
"""

from fastapi import APIRouter

from app.api.v1.analysis import router as sca_router
from app.api.v1.auth import router as auth_router
from app.api.v1.history import router as history_router

api_router = APIRouter()

# SCA endpoints live at  /api/v1/sca/*
api_router.include_router(sca_router, prefix="/sca", tags=["sca"])

# Auth endpoints live at /api/v1/auth/*
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# History endpoints live at /api/v1/history/*
api_router.include_router(history_router, prefix="/history", tags=["history"])
