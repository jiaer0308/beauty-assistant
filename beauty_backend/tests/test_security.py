#!/usr/bin/env python3
"""
Tests for security utilities.
"""

import pytest
from datetime import timedelta
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_token_payload
)

def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_token_creation_and_validation():
    data = {"sub": "user123", "role": "guest"}
    token = create_access_token(data)
    assert isinstance(token, str)
    
    payload = get_token_payload(token)
    assert payload["sub"] == "user123"
    assert payload["role"] == "guest"
    assert "exp" in payload

def test_jwt_token_expiration():
    # Test with very short expiration
    data = {"sub": "user123"}
    # Using a negative delta to simulate immediate expiration
    token = create_access_token(data, expires_delta=timedelta(seconds=-10))
    payload = get_token_payload(token)
    assert payload is None

def test_invalid_token():
    payload = get_token_payload("invalid_token_string")
    assert payload is None
