# Next Steps After Adding Route

## After Clicking "Add route"

### Step 1: Configure CORS
1. In the left sidebar, click on **"CORS"**
2. Click **"Configure"** button
3. Set the following:
   - **Access-Control-Allow-Origin:** `*` (or your specific domain)
   - **Access-Control-Allow-Methods:** Select all methods (GET, POST, PUT, DELETE, PATCH, OPTIONS)
   - **Access-Control-Allow-Headers:** 
     ```
     Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
     ```
   - **Access-Control-Allow-Credentials:** Leave unchecked
4. Click **"Save"**

### Step 2: Review Your API
1. Click on **"Routes"** in the left sidebar
2. You should see your route: **ANY /{proxy+}** → **tracker**
3. Click on the route to verify it's configured correctly

### Step 3: Get Your API Endpoint
1. Click on **"Stages"** in the left sidebar
2. Click on **"$default"** stage
3. Copy the **"Invoke URL"** - this is your base API endpoint
4. Your full endpoint format: `https://xxxxx.execute-api.ap-south-1.amazonaws.com/{your-path}`

### Step 4: Update Frontend (if needed)
Your `api.js` already has the correct endpoint:
```javascript
export const API_BASE_URL = "https://4pfbkvforf.execute-api.ap-south-1.amazonaws.com";
```

Make sure your API calls use this base URL:
```javascript
// Example API call
fetch(`${API_BASE_URL}/api/students`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
```

### Step 5: Test Your API
1. Go to **"Stages"** → **"$default"**
2. Find your **"Invoke URL"**
3. Test in browser or Postman:
   ```
   GET https://4pfbkvforf.execute-api.ap-south-1.amazonaws.com/api/test
   ```

### Step 6: Verify Lambda Permissions
Make sure your Lambda function "tracker" allows API Gateway to invoke it:
1. Go to **Lambda Console** → Select **"tracker"** function
2. Go to **"Configuration"** → **"Permissions"**
3. Under **"Resource-based policy"**, verify there's a policy allowing:
   - **Principal:** `apigateway.amazonaws.com`
   - **Action:** `lambda:InvokeFunction`
   - **Source ARN:** Your API Gateway ARN

If missing, add it:
- Click **"Add permissions"**
- Select **"AWS service"**
- Service: **"API Gateway"**
- Statement ID: Auto-generated
- Source ARN: `arn:aws:execute-api:ap-south-1:474833638797:*/*/*`
- Click **"Save"**

---

## Your Current Configuration ✅

- **Method:** ANY ✓
- **Resource Path:** /{proxy+} ✓
- **Integration Target:** tracker (Lambda function) ✓
- **API Endpoint:** https://4pfbkvforf.execute-api.ap-south-1.amazonaws.com ✓

---

## Important Notes

1. **Proxy Integration:** With `/{proxy+}`, all paths are forwarded to your Lambda
   - Example: `/api/students` → Lambda receives `/api/students` in the event
   - Your Lambda needs to parse the `event.path` to handle different routes

2. **Lambda Event Structure:** Your Lambda will receive:
   ```json
   {
     "path": "/api/students",
     "httpMethod": "GET",
     "headers": {...},
     "body": "...",
     "queryStringParameters": {...}
   }
   ```

3. **CORS:** Make sure CORS is configured, otherwise browser requests will fail

4. **Deployment:** After making changes, they're automatically deployed to `$default` stage

---

## Troubleshooting

### If you get CORS errors:
- Verify CORS is configured in API Gateway
- Check that your frontend domain matches the allowed origin

### If you get 403 Forbidden:
- Check Lambda resource-based policy
- Verify API Gateway has permission to invoke Lambda

### If you get 502 Bad Gateway:
- Check Lambda function logs in CloudWatch
- Verify Lambda function is working correctly
- Check Lambda timeout settings (should be sufficient for your use case)

### If routes don't work:
- Verify your Lambda function handles the proxy integration correctly
- Check that you're parsing `event.path` correctly in Lambda
- Test with different paths to ensure `/{proxy+}` is working









