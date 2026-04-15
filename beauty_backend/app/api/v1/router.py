#!/usr/bin/env python3
"""
API v1 Main Router

Aggregates all v1 endpoint routers under a single prefix.
Add new feature routers here as the app grows.
"""

from fastapi import APIRouter

from app.api.v1.analysis import router as sca_router
from app.api.v1.auth import router as auth_router
from app.api.v1.cosmetics import router as cosmetics_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.favorites import router as favorites_router
from app.api.v1.history import router as history_router

api_router = APIRouter()

# Dashboard endpoints live at /api/v1/dashboard/*
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

# SCA endpoints live at  /api/v1/sca/*
api_router.include_router(sca_router, prefix="/sca", tags=["sca"])

# Auth endpoints live at /api/v1/auth/*
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# History endpoints live at /api/v1/history/*
api_router.include_router(history_router, prefix="/history", tags=["history"])

# Cosmetics knowledge-base endpoints live at /api/v1/cosmetics/*
api_router.include_router(cosmetics_router, prefix="/cosmetics", tags=["cosmetics"])

# Favorites endpoints live at /api/v1/favorites/*
api_router.include_router(favorites_router, prefix="/favorites", tags=["favorites"])


