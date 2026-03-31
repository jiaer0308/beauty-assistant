# Design Spec: Quiz Model Synchronization (Backend-Frontend)

**Date:** 2026-03-25
**Topic:** Aligning Backend QuizData schema and QuizEngine logic with the 9-step Flutter onboarding quiz.
**Status:** Draft

## 1. Goal
Ensure the FastAPI backend and Flutter frontend share a single, synchronized 9-step quiz model. This involves renaming backend fields to match Flutter keys exactly and adding the missing 4 preference/style questions.

## 2. 1:1 Field Mapping
The backend `QuizData` model will be updated to match the Flutter `state.answers` keys exactly.

| Flutter Key (`onboarding_quiz_screen.dart`) | Backend Field (`app/schemas/sca.py`) | Type | Usage |
| :--- | :--- | :--- | :--- |
| `skin_type` | `skin_type` | `str | None` | Logging / Filtering |
| `sun_reaction` | `sun_reaction` | `str | None` | **SCA Adjustment** |
| `wrist_vein` | `wrist_vein` | `str | None` | **SCA Adjustment** (Warm/Cool) |
| `hair_color` | `hair_color` | `str | None` | **SCA Adjustment** (Depth) |
| `jewelry` | `jewelry` | `str | None` | **SCA Adjustment** (Warm/Cool) |
| `foundation_coverage` | `foundation_coverage` | `str | None` | Recommendation Filter |
| `makeup_finish` | `makeup_finish` | `str | None` | Recommendation Filter |
| `skin_concerns` | `skin_concerns` | `List[str] | None` | Recommendation Filter |
| `lip_style` | `lip_style` | `str | None` | Recommendation Filter |

## 3. Component Changes

### A. `app/schemas/sca.py`
- Refactor `QuizData` class to use the 9 fields listed above.
- Remove old field names: `vein_color`, `natural_hair_color`, `jewelry_preference`.
- Add new fields: `foundation_coverage`, `makeup_finish`, `skin_concerns`, `lip_style`.

### B. `app/services/quiz_engine.py`
- Update `_build_quiz_adjustment` to call handlers with new field names.
- Rename handler methods and internal logic to use **exact Flutter strings**:
    - **`wrist_vein`**: `Blue or Purple`, `Green or Olive`, `Mixed / Unsure`
    - **`jewelry`**: `Silver / White Gold`, `Yellow Gold`, `Rose Gold`
    - **`sun_reaction`**: `Burn easily, rarely tan`, `Burn first, then tan`, `Tan easily, rarely burn`
    - **`hair_color`**: `Black`, `Warm Brown`, `Ashy Blonde`, `Golden Blonde`
- Ensure mappings for new option strings (e.g., "Silver / White Gold" instead of "silver").

### C. `app/services/recommendation_mapper.py`
- Update dynamic filtering logic to utilize the 4 new preference fields:
    - **Coverage:** If `foundation_coverage == 'Sheer / Light'`, filter Foundations.
    - **Skin Type:** If `skin_type == 'Oily'`, exclude "Cream" categories.
    - **Lip Style:** If `lip_style == 'MLBB (Nudes/Balms)'`, filter for nudes/balms.

## 4. Testing & Validation
- **Schema Validation:** Verify the API accepts the full 9-field JSON payload from Flutter.
- **SCA Accuracy:** Confirm `wrist_vein` and `jewelry` still correctly influence the 12-season scoring.
- **Filtering Logic:** Verify `foundation_coverage` and `skin_type` correctly prune the `cosmetics` list in the response.
