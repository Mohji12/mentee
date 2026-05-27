# How to Create API Gateway HTTP API Trigger for Lambda Function

## Step-by-Step Console Instructions

### Step 1: Navigate to API Gateway Console
1. Log in to AWS Console: https://console.aws.amazon.com
2. In the search bar at the top, type **"API Gateway"** and click on **API Gateway** service
3. You'll be taken to the API Gateway Dashboard

### Step 2: Create HTTP API
1. Click on **"Create API"** button (usually a big orange button)
2. Under **"Choose an API type"**, select **"HTTP API"** (not REST API)
3. Click **"Build"** button

### Step 3: Configure API Gateway
1. You'll see the **"Create an HTTP API"** page with several steps:

#### Step 3.1: Integrations
- Click **"Add integration"**
- Select **"Lambda"** as the integration type
- In the **"Lambda function"** dropdown, select your Lambda function (e.g., `mentee-function` or your function name)
- **Important:** If you see a warning about enabling function URL, you can ignore it or enable it later
- Click **"Next"**

#### Step 3.2: Configure Routes
- **Method:** Select **"ANY"** from the dropdown
- **Resource path:** Type `/{proxy+}` (this allows all paths)
- Click **"Next"**

#### Step 3.3: Configure Stages
- **Stage name:** Leave as **"$default"** (or enter a custom name)
- Click **"Next"**

#### Step 3.4: Review and Create
- Review your configuration:
  - Integration: Lambda function
  - Route: ANY /{proxy+}
  - Stage: $default
- Click **"Create"**

### Step 4: Configure CORS (Cross-Origin Resource Sharing)

1. After the API is created, you'll see your API details page
2. In the left sidebar, click on **"CORS"** (under your API name)
3. Click **"Configure"** button
4. Configure CORS settings:
   - **Access-Control-Allow-Origin:** Enter `*` (for all origins) or your specific domain (e.g., `https://yourdomain.com`)
   - **Access-Control-Allow-Methods:** Select:
     - GET
     - POST
     - PUT
     - DELETE
     - PATCH
     - OPTIONS
   - **Access-Control-Allow-Headers:** Enter: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
   - **Access-Control-Allow-Credentials:** Leave unchecked (or check if needed)
   - **Access-Control-Max-Age:** Enter `3600` (or leave default)
5. Click **"Save"**

### Step 5: Configure Authorization (Set to NONE)

1. In the left sidebar, click on **"Routes"**
2. Click on your route: **ANY /{proxy+}**
3. In the route details, find **"Authorization"** section
4. Click **"Attach"** or **"Edit"**
5. Select **"NONE"** from the authorization dropdown
6. Click **"Save"**

### Step 6: Get Your API Endpoint

1. In the left sidebar, click on **"Stages"**
2. Click on **"$default"** stage
3. You'll see your **"Invoke URL"** - this is your API endpoint
   - Format: `https://xxxxx.execute-api.ap-south-1.amazonaws.com`
4. Your full endpoint will be: `https://xxxxx.execute-api.ap-south-1.amazonaws.com/{proxy+}`
   - Replace `{proxy+}` with your actual path (e.g., `/api/users`)

### Step 7: Grant API Gateway Permission to Invoke Lambda

**Important:** Make sure your Lambda function allows API Gateway to invoke it:

1. Go to **Lambda Console** → Select your function
2. Go to **"Configuration"** tab → **"Permissions"**
3. Under **"Resource-based policy statements"**, check if there's a policy allowing `apigateway.amazonaws.com`
4. If not present, you may need to add it manually:
   - Go to **"Configuration"** → **"Permissions"** → **"Resource-based policy"**
   - Click **"Add permissions"**
   - Select **"AWS service"**
   - Service: **"API Gateway"**
   - Statement ID: Auto-generated or custom
   - Source ARN: Your API Gateway ARN (you can use wildcard: `arn:aws:execute-api:ap-south-1:474833638797:*/*/*`)
   - Click **"Save"**

---

## Quick Summary Checklist

- [ ] Created HTTP API (not REST API)
- [ ] Added Lambda integration
- [ ] Configured route: ANY /{proxy+}
- [ ] Set stage: $default
- [ ] Configured CORS (enabled)
- [ ] Set Authorization: NONE
- [ ] Got API endpoint URL
- [ ] Verified Lambda permissions for API Gateway

---

## API Endpoint Usage Examples

After setup, your endpoints will be:

```
Base URL: https://xxxxx.execute-api.ap-south-1.amazonaws.com

Examples:
- GET  https://xxxxx.execute-api.ap-south-1.amazonaws.com/api/students
- POST https://xxxxx.execute-api.ap-south-1.amazonaws.com/api/login
- PUT  https://xxxxx.execute-api.ap-south-1.amazonaws.com/api/update
```

---

## Troubleshooting

### If Lambda function is not found in integration dropdown:
- Make sure your Lambda function exists in the same region (ap-south-1)
- Check that you have permissions to view Lambda functions
- Try refreshing the page

### If you get 403 Forbidden:
- Check Lambda resource-based policy allows API Gateway
- Verify the API Gateway has permission to invoke Lambda

### If CORS errors occur:
- Double-check CORS configuration
- Verify allowed origins match your frontend domain
- Check that OPTIONS method is allowed

### If you get 502 Bad Gateway:
- Check Lambda function logs in CloudWatch
- Verify Lambda function is working correctly
- Check Lambda timeout settings

---

## Additional Configuration (Optional)

### Enable Detailed Metrics:
1. Go to **"Monitoring"** tab in API Gateway
2. Enable **"Detailed CloudWatch metrics"**

### Add Custom Domain:
1. Go to **"Custom domain names"** in left sidebar
2. Click **"Create"**
3. Enter your domain name
4. Configure DNS records as instructed

---

## Your Configuration Summary

Based on your example:
- **API Type:** HTTP API
- **Authorization:** NONE
- **CORS:** Enabled
- **Method:** ANY
- **Resource Path:** /{proxy+}
- **Stage:** $default
- **Integration:** Lambda function
- **Region:** ap-south-1









