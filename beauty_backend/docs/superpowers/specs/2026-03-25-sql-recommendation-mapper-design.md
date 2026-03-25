# Design Spec: SQL-Based Recommendation Mapper with Eager Loading & Dynamic Filtering

**Date:** 2026-03-25
**Topic:** Migrating RecommendationMapper from JSON to SQL with Eager Loading, Category Limiting, and Quiz-Based Filtering
**Status:** Draft

## 1. Goal
Transition the `RecommendationMapper` from a static JSON-based lookup to a dynamic, SQL-driven service. The system must:
1. Solve the N+1 query problem using eager loading.
2. Limit results to a maximum of 5 items per category.
3. Apply dynamic filters based on user quiz data (coverage, skin type, etc.).

## 2. Architecture & Data Flow
The `RecommendationMapper` will be a stateless service that performs live queries against the MySQL database. It will be integrated into the `SCAWorkflowService`.

### Components
- **Service:** `app/services/recommendation_mapper.py`
- **Models:** `app/domain/entities/knowledge_base.py`
- **Consumer:** `app/services/sca_workflow_service.py`

## 3. Implementation Details

### Method: `get_recommendations(season_name: str, db: Session, quiz_data: dict = None)`

#### Step 1: Season Resolution
Find the `Season` entity by its name string.
```python
season = db.query(Season).filter(Season.name == season_name).first()
```

#### Step 2: Dynamic Cosmetic Query with Eager Loading
Build a base query for `CosmeticProduct` joined with `CosmeticSeasonMapping`.

```python
query = (
    db.query(CosmeticProduct)
    .join(CosmeticSeasonMapping)
    .filter(
        CosmeticSeasonMapping.season_id == season.id,
        CosmeticProduct.is_active == True
    )
    .options(
        joinedload(CosmeticProduct.brand),
        joinedload(CosmeticProduct.category)
    )
)
```

#### Step 3: Dynamic Filtering (Task 3)
Apply filters based on `quiz_data`:

*   **Coverage Logic:** If `quiz_data.get('foundation_coverage') == 'Sheer/Light'`, filter products in the "Foundation" category to only include those named 'BB/CC Cream'.
*   **Skin Type Logic:** If `quiz_data.get('skin_type') == 'Oily'`, exclude any `Category.name` containing the string "Cream".

```python
if quiz_data:
    # Coverage filtering
    if quiz_data.get('foundation_coverage') == 'Sheer/Light':
        # logic to specifically filter foundations while keeping other categories intact
        # (e.g. using an OR condition or post-processing)
        pass

    # Skin type filtering
    if quiz_data.get('skin_type') == 'Oily':
        query = query.join(Category).filter(~Category.name.contains('Cream'))
```

#### Step 4: Result Limiting (Task 2)
To ensure performance and manageable payload size, limit results to 5 items **per category**.
*   **Approach:** Fetch all filtered results and group/slice in Python.
*   **Logic:**
    1.  Fetch `all_cosmetics = query.all()`.
    2.  Group by `category.name`.
    3.  Slice each group list to `[:5]`.

#### Step 5: Color Retrieval
Query `SeasonColor` for the resolved season, eagerly loading color details.

## 4. Output Schema
The returned dictionary will strictly follow this structure:
```json
{
  "best_colors": [{"name": "...", "hex": "..."}],
  "neutral_colors": [{"name": "...", "hex": "..."}],
  "avoid_colors": [{"name": "...", "hex": "..."}],
  "cosmetics": [
    {
      "category": "...",
      "brand": "...",
      "name": "...",
      "shade": "...",
      "hex": "...",
      "image_url": "..."
    }
  ]
}
```

## 5. Testing & Validation
- **Category Limit:** Verify no more than 5 items exist for any single category in the `cosmetics` list.
- **Dynamic Filter:** Test that 'Oily' skin type removes 'Cream' products.
- **Performance:** Verify eager loading prevents N+1 queries for brands and categories.
