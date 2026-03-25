# Seasonal Color & Cosmetics Knowledge Base Database Design

## 1. Understanding Summary
*   **What**: A normalized MySQL database architecture replacing the static `knowledge_base.json` for the seasonal color analysis (SCA) system.
*   **Why**: To allow the cosmetic product list to grow dynamically, enabling advanced multi-dimensional filtering, while keeping base seasonal color palettes stable.
*   **Who**: Backend developers/APIs fetching accurate recommendations, and administrators managing cosmetics.
*   **Key Constraints**: Efficient multi-dimensional filtering (by category, brand) and supporting Many-to-Many mappings between cosmetics and seasons.
*   **Explicit Non-Goals**: This is NOT an e-commerce database; it does not model inventory, shopping carts, or financial transactions.

## 2. Assumptions
*   **Scale**: Small to medium (thousands of products, 12 static seasons). A single MySQL database instance is sufficient without distributed sharding.
*   **Performance**: Extremely high read-to-write ratio. Queries will heavily rely on traversing foreign keys, requiring indexing on read paths.
*   **Data Integrity**: Brands and categories must be distinct normalized tables (or strict enums) to prevent fragmented data (e.g., "MAC" vs "M.A.C").
*   **Soft Deletes**: Inactive/discontinued cosmetics will be flagged `is_active=false` rather than permanently deleted so historical user records aren't broken.

## 3. Final Design (Entity Relationship)

* **Season**: `id` (PK), `name` (e.g., "Deep Winter"), `description`.
* **Color**: `id` (PK), `name` (e.g., "True Red"), `hex_code` (e.g., "#C8102E").
* **SeasonColorMapping**: `season_id` (FK), `color_id` (FK), `category_type` (ENUM: 'best', 'neutral', 'avoid').
* **Brand**: `id` (PK), `name` (e.g., "MAC"), `is_active` (boolean).
* **Category**: `id` (PK), `name` (e.g., "Lipstick").
* **CosmeticProduct**: `id` (PK), `brand_id` (FK), `category_id` (FK), `shade_name` (e.g., "Ruby Woo"), `hex_code` (e.g., "#9B111E"), `image_url` (e.g., "https://..."), `is_active` (boolean).
* **CosmeticSeasonMapping**: `season_id` (FK), `cosmetic_id` (FK).

## 4. Decision Log
1. **Database Type**: Relational Database (MySQL)
   * *Alternatives considered*: Document Store (MongoDB), Flat JSON files.
   * *Reasoning*: Relational logic perfectly matches the advanced filtering requirements for cosmetics, ensuring consistent naming (Brands, Categories) and robust joins.
2. **Cosmetic-To-Season Mapping**: Many-to-Many Relationship
   * *Alternatives considered*: One-to-Many (strict mapping of one shade to only one season).
   * *Reasoning*: The exact same cosmetic product can legitimately look good on multiple closely related seasons (e.g., Deep Winter and Clear Winter). A junction table avoids duplicating cosmetic items.
3. **Foundation Integration**: Unified Table (Approach A)
   * *Reasoning*: Simplified maintenance by grouping all recommended cosmetics together. Foundations are treated as a standard `Category`.
4. **Data Trimming**: Removed tags and pricing
   * *Reasoning*: Per user requirement, tags and price data were deemed unnecessary for the core color recommendation engine, reducing database complexity.
5. **Shade Granularity**: One shade per CosmeticProduct row
   * *Reasoning*: Since foundation "products" have multiple "shades" with distinct color properties (hex), each shade is treated as a unique recommendation unit.
6. **Seeding Strategy**: Python Migration Script (Approach 1)
   * *Reasoning*: Offers the most flexibility for complex data transformations (like unnesting shades) while maintaining high reliability and error handling.
