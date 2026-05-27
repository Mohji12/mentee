# Troubleshooting SWOT Analysis Update Issues

## Common Issues and Solutions

### Issue 1: Column Type is Still VARCHAR(255)
**Symptom:** Data gets truncated to 255 characters

**Solution:**
```sql
ALTER TABLE swot MODIFY COLUMN swot_analysis TEXT;
```

### Issue 2: Record Doesn't Exist
**Symptom:** UPDATE affects 0 rows

**Solution:** Check if record exists first:
```sql
SELECT * FROM swot WHERE student_usn = '23MSRDS018';
```

If no record exists, use INSERT instead:
```sql
INSERT INTO swot (student_usn, swot_analysis) 
VALUES ('23MSRDS018', '...your text...');
```

### Issue 3: SQL Syntax Errors with Special Characters
**Symptom:** Error about quotes or special characters

**Solution:** Use the Python script (`update_swot_python.py`) which handles escaping automatically

### Issue 4: Connection Issues
**Symptom:** Can't connect to database

**Solution:** 
1. Check database credentials in `app/db/database.py`
2. Verify database is running
3. Check network/firewall settings

## Recommended Approach

### Option 1: Use Python Script (Recommended)
```bash
python update_swot_python.py
```

This script:
- ✅ Automatically checks and alters column type if needed
- ✅ Handles escaping properly
- ✅ Checks if record exists and uses UPDATE or INSERT accordingly
- ✅ Verifies the update was successful

### Option 2: Use SQL File Step by Step
1. Run `alter_swot_column.sql` first
2. Check if record exists: `SELECT * FROM swot WHERE student_usn = '23MSRDS018';`
3. Run the UPDATE query from `update_swot_analysis.sql`

## Verification

After updating, verify the data:
```sql
SELECT 
    student_usn,
    LENGTH(swot_analysis) as text_length,
    LEFT(swot_analysis, 200) as preview
FROM swot 
WHERE student_usn = '23MSRDS018';
```

Expected text_length should be around 3500+ characters (not 255).





