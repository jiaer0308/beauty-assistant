#!/usr/bin/env python3
"""
Knowledge base entities for seasonal color analysis and cosmetics.
"""

import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, func, Table
from sqlalchemy.orm import relationship

from app.core.database import Base


class CategoryType(str, enum.Enum):
    BEST = "best"
    NEUTRAL = "neutral"
    AVOID = "avoid"


class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    colors = relationship("SeasonColor", back_populates="season")
    cosmetics = relationship("CosmeticProduct", secondary="cosmetic_season_mappings", back_populates="seasons")


class Color(Base):
    __tablename__ = "colors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    hex_code = Column(String(7), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    seasons = relationship("SeasonColor", back_populates="color")


class SeasonColor(Base):
    __tablename__ = "season_colors"

    season_id = Column(Integer, ForeignKey("seasons.id"), primary_key=True)
    color_id = Column(Integer, ForeignKey("colors.id"), primary_key=True)
    category_type = Column(Enum(CategoryType, values_callable=lambda obj: [e.value for e in obj]), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    season = relationship("Season", back_populates="colors")
    color = relationship("Color", back_populates="seasons")


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    products = relationship("CosmeticProduct", back_populates="brand")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    products = relationship("CosmeticProduct", back_populates="category")


class CosmeticProduct(Base):
    __tablename__ = "cosmetic_products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    product_name = Column(String(150), nullable=False)
    shade_name = Column(String(150), nullable=False)
    hex_code = Column(String(7), nullable=True)
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    seasons = relationship("Season", secondary="cosmetic_season_mappings", back_populates="cosmetics")


class CosmeticSeasonMapping(Base):
    __tablename__ = "cosmetic_season_mappings"

    season_id = Column(Integer, ForeignKey("seasons.id"), primary_key=True)
    cosmetic_id = Column(Integer, ForeignKey("cosmetic_products.id"), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
