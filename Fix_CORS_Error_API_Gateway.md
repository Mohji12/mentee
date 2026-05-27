# Fix CORS Error with API Gateway

## Problem
- ✅ FastAPI backend has CORS configured (works with Swagger)
- ❌ API Gateway is blocking CORS requests from frontend
- Need to configure CORS in API Gateway

---

## Solution: Configure CORS in API Gateway

### Step 1: Enable CORS in API Gateway

1. Go to **API Gateway Console**
2. Select your API (the one with endpoint: `753cnrn9q8.execute-api.ap-south-1.amazonaws.com`)
3. In the left sidebar, click on **"CORS"**
4. Click **"Configure"** button

### Step 2: Set CORS Configuration

Configure the following:

**Access-Control-Allow-Origin:**
- Enter: `*` (for all origins)
- OR enter your specific frontend domain: `http://localhost:3000` (for development)
- OR: `https://yourdomain.com` (for production)

**Access-Control-Allow-Methods:**
- Select ALL of these:
  - ✅ GET
  - ✅ POST
  - ✅ PUT
  - ✅ DELETE
  - ✅ PATCH
  - ✅ OPTIONS (IMPORTANT for preflight requests)

**Access-Control-Allow-Headers:**
- Enter this (comma-separated, no spaces):
```
Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Accept,Origin
```

**Access-Control-Allow-Credentials:**
- Leave **UNCHECKED** (if using `*` for origin)
- OR **CHECK** if using specific domain

**Access-Control-Max-Age:**
- Enter: `3600` (or leave default)

### Step 3: Save CORS Configuration

1. Click **"Save"** button
2. Wait a few seconds for changes to apply

### Step 4: Deploy the API

1. Click **"Deploy"** button (top right)
2. Select your stage (e.g., `default` or `$default`)
3. Click **"Deploy"**

---

## Alternative: Handle CORS in Lambda (If API Gateway CORS doesn't work)

If API Gateway CORS still doesn't work, your Lambda function needs to handle OPTIONS requests.

### Update Lambda Function to Handle CORS

Your FastAPI app should already handle this, but verify your Lambda handler returns proper CORS headers for OPTIONS requests.

The FastAPI CORS middleware should handle this, but make sure your Lambda function is properly invoking it.

---

## Step-by-Step: Complete CORS Setup

### 1. API Gateway CORS Configuration

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Accept,Origin
Access-Control-Max-Age: 3600
```

### 2. Verify FastAPI CORS (Already configured ✅)

Your `app/main.py` already has:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This is correct! ✅

### 3. Test CORS

After configuring, test with:

**Browser Console:**
```javascript
fetch('https://753cnrn9q8.execute-api.ap-south-1.amazonaws.com/api/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ email: 'test', password: 'test' })
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

---

## Common CORS Errors and Fixes

### Error: "Access-Control-Allow-Origin header missing"
**Fix:** Enable CORS in API Gateway (Step 1-3 above)

### Error: "Preflight request failed"
**Fix:** Make sure OPTIONS method is enabled in CORS configuration

### Error: "Credentials not allowed"
**Fix:** 
- If using `*` for origin, uncheck "Allow credentials"
- If using specific domain, check "Allow credentials"

### Error: "Header not allowed"
**Fix:** Add the missing header to "Access-Control-Allow-Headers" in API Gateway

---

## Quick Checklist

- [ ] CORS configured in API Gateway
- [ ] OPTIONS method enabled
- [ ] All required headers added
- [ ] API deployed after CORS changes
- [ ] Tested with browser console
- [ ] Verified FastAPI CORS is working (already ✅)

---

## Important Notes

1. **API Gateway CORS vs FastAPI CORS:**
   - API Gateway CORS handles preflight (OPTIONS) requests
   - FastAPI CORS handles actual request CORS headers
   - Both need to be configured

2. **After changing CORS:**
   - Always **Deploy** the API for changes to take effect
   - Wait 10-30 seconds for changes to propagate

3. **Testing:**
   - Clear browser cache
   - Try in incognito mode
   - Check browser Network tab for CORS headers

---

## If Still Not Working

1. **Check Browser Console:**
   - Open DevTools (F12)
   - Go to Network tab
   - Look at the failed request
   - Check Response Headers for CORS headers

2. **Verify API Gateway Deployment:**
   - Make sure you deployed after CORS changes
   - Check the stage is active

3. **Test with curl:**
   ```bash
   curl -X OPTIONS https://753cnrn9q8.execute-api.ap-south-1.amazonaws.com/api/login \
     -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -v
   ```
   Should return CORS headers in response

4. **Check Lambda Logs:**
   - Go to CloudWatch → Log groups
   - Find your Lambda function logs
   - Check if requests are reaching Lambda









