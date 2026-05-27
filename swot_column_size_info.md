# SWOT Analysis Column Size Information

## Current Column Type
- **Database Schema**: `VARCHAR(255)` = **255 characters maximum**
- **SQLAlchemy Model**: `String(1000)` = 1000 characters (but database limit is 255)

## Character Limits by Data Type

### VARCHAR Options:
- `VARCHAR(255)` = **255 characters** (current)
- `VARCHAR(500)` = **500 characters**
- `VARCHAR(1000)` = **1000 characters**
- `VARCHAR(2000)` = **2000 characters**
- `VARCHAR(5000)` = **5000 characters**
- Maximum `VARCHAR` in MySQL = **65,535 characters** (but not recommended for such large text)

### TEXT Options (Recommended for long text):
- `TINYTEXT` = **255 characters** (same as VARCHAR(255))
- `TEXT` = **65,535 characters** (64 KB) ✅ **Recommended**
- `MEDIUMTEXT` = **16,777,215 characters** (16 MB)
- `LONGTEXT` = **4,294,967,295 characters** (4 GB)

## Recommendation

For SWOT analysis text (which can be quite long), use **`TEXT`** type:
- Supports up to **65,535 characters** (64 KB)
- More than enough for SWOT analysis content
- Better performance for variable-length text
- No need to specify length

## SQL to Change Column Type

```sql
-- Change to TEXT (recommended - 65,535 characters)
ALTER TABLE swot MODIFY COLUMN swot_analysis TEXT;

-- OR if you want a specific VARCHAR size:
ALTER TABLE swot MODIFY COLUMN swot_analysis VARCHAR(5000);
```

## Your Current SWOT Text Length
Your SWOT analysis text is approximately **3,500+ characters**, which exceeds the current 255 character limit.





