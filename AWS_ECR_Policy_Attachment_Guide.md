# How to Attach ECR Policy to Lambda Execution Role

## Step-by-Step Console Instructions

### Step 1: Navigate to IAM Console
1. Log in to AWS Console: https://console.aws.amazon.com
2. In the search bar at the top, type **"IAM"** and click on **IAM** service
3. You'll be taken to the IAM Dashboard

### Step 2: Find Your Lambda Execution Role
1. In the left sidebar, click on **"Roles"**
2. In the search box, type: **mentee-role-o2dc9366**
3. Click on the role name **mentee-role-o2dc9366** to open it

### Step 3: Add Inline Policy (Recommended Method)

#### Option A: Create Inline Policy (Recommended)
1. In the role details page, click on the **"Permissions"** tab
2. Scroll down to find **"Permissions policies"** section
3. Click on **"Add permissions"** dropdown button
4. Select **"Create inline policy"**

5. You'll see a visual policy editor. Click on **"JSON"** tab at the top

6. Delete any existing content and paste this JSON:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage"
            ],
            "Resource": "arn:aws:ecr:ap-south-1:474833638797:repository/mentee"
        }
    ]
}
```

7. Click **"Next"** button
8. Give the policy a name: **"ECR-Pull-Permissions"** (or any name you prefer)
9. Click **"Create policy"** button

### Step 4: Verify the Policy
1. You should see a success message
2. Go back to the **"Permissions"** tab
3. You should now see your new inline policy listed under **"Permissions policies"**

---

## Alternative: Attach AWS Managed Policy (If Available)

If you prefer using AWS managed policies:

1. In the role details page, click on **"Permissions"** tab
2. Click on **"Add permissions"** dropdown
3. Select **"Attach policies"**
4. In the search box, type: **"ECR"**
5. Look for policies like:
   - **AmazonEC2ContainerRegistryReadOnly** (if available)
6. Check the box next to the policy
7. Click **"Add permissions"** button

**Note:** The managed policy might have broader permissions than needed. The inline policy method above is more secure as it only grants the specific permissions needed.

---

## Quick Summary

1. Go to IAM Console → Roles
2. Search for: **mentee-role-o2dc9366**
3. Click on the role
4. Go to **Permissions** tab
5. Click **Add permissions** → **Create inline policy**
6. Switch to **JSON** tab
7. Paste the policy JSON (replace `<your-ecr-repository-name>` with `mentee`)
8. Name it and create

---

## Policy Details

**Role Name:** mentee-role-o2dc9366  
**Repository:** mentee  
**Region:** ap-south-1  
**Account ID:** 474833638797

**Full Resource ARN:**
```
arn:aws:ecr:ap-south-1:474833638797:repository/mentee
```

---

## Troubleshooting

### If you can't find the role:
- Make sure you're in the correct AWS region (ap-south-1)
- Check if the role name is exactly: `mentee-role-o2dc9366`
- Verify you have IAM permissions to view roles

### If policy creation fails:
- Check that the JSON is valid (no syntax errors)
- Ensure you have permissions to create inline policies
- Verify the repository name is correct: `mentee`

### After adding the policy:
- Wait 1-2 minutes for permissions to propagate
- Try deploying your Lambda function again
- Check CloudWatch Logs if there are still errors









