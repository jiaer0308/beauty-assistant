# SQL-Based Recommendation Mapper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transition `RecommendationMapper` from JSON to SQL with eager loading, category limiting (max 5), and quiz-based filtering.

**Architecture:** Stateless service using SQLAlchemy for live queries. Uses `joinedload` to prevent N+1 issues and Python-side grouping for category limits.

**Tech Stack:** Python, SQLAlchemy, MySQL.

---

### Task 1: Refactor RecommendationMapper to SQL Base

**Files:**
- Modify: `app/services/recommendation_mapper.py`
- Test: `tests/services/test_recommendation_mapper.py`

- [ ] **Step 1: Write a failing test for SQL-based retrieval**
- [ ] **Step 2: Update imports and remove JSON logic in `recommendation_mapper.py`**
- [ ] **Step 3: Implement `get_recommendations` with Season lookup and Eager Loading**
- [ ] **Step 4: Run test to verify basic SQL retrieval works**
- [ ] **Step 5: Commit**

### Task 2: Implement Category Limiting (Task 2)

**Files:**
- Modify: `app/services/recommendation_mapper.py`
- Test: `tests/services/test_recommendation_mapper.py`

- [ ] **Step 1: Write a test case with >5 products in one category**
- [ ] **Step 2: Implement grouping and slicing logic in `get_recommendations`**
- [ ] **Step 3: Run test to verify limit of 5 items per category**
- [ ] **Step 4: Commit**

### Task 3: Implement Dynamic Quiz Filtering (Task 3)

**Files:**
- Modify: `app/services/recommendation_mapper.py`
- Test: `tests/services/test_recommendation_mapper.py`

- [ ] **Step 1: Write test cases for 'Sheer/Light' coverage and 'Oily' skin type**
- [ ] **Step 2: Implement dynamic `.filter()` conditions in `get_recommendations`**
- [ ] **Step 3: Run tests to verify filtering logic**
- [ ] **Step 4: Commit**

### Task 4: Integrate with SCAWorkflowService

**Files:**
- Modify: `app/services/sca_workflow_service.py`

- [ ] **Step 1: Update `SCAWorkflowService.analyze` to pass `db` and `quiz_data`**
- [ ] **Step 2: Verify the end-to-end flow with an integration test or manual check**
- [ ] **Step 3: Commit**
