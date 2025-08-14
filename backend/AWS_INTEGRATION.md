# AWS Integration for Campaign Storage

This document describes the AWS integration for storing campaign artifacts, metadata, and state information using Amazon S3 and DynamoDB.

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Campaign      │    │   AWS S3        │    │   DynamoDB      │
│   Generation    │───▶│   Bucket        │    │   Table         │
│   System        │    │   (campaign-    │    │   (campaigns)   │
│                 │    │    outputs)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 **S3 Storage Structure**

### **Bucket Organization**
```
s3://campaign-outputs/
├── campaigns/
│   ├── campaign_20241201_120000_123456/
│   │   ├── website/
│   │   │   └── index.html                    # Campaign website
│   │   ├── pdf/
│   │   │   └── campaign_report.pdf           # Campaign PDF report
│   │   ├── artifacts/
│   │   │   └── workflow_state.json           # Complete workflow state
│   │   └── metadata/
│   │       └── campaign_metadata.json        # Campaign metadata
│   └── campaign_20241201_130000_789012/
│       └── ...
```

### **File Types Stored**
- **Website HTML**: Complete campaign website with styling
- **PDF Reports**: Generated campaign reports and summaries
- **Workflow State**: Complete AI agent workflow state and artifacts
- **Metadata**: Campaign brief, progress logs, agent interactions

## 🗄️ **DynamoDB Schema**

### **Table: campaigns**
```json
{
  "campaign_id": "campaign_20241201_120000_123456",
  "user_id": "username",
  "campaign_name": "Product Launch Campaign",
  "status": "completed",
  "created_at": "2024-12-01T12:00:00",
  "completed_at": "2024-12-01T12:03:20",
  "execution_time": 200.5,
  "s3_website_url": "https://campaign-outputs.s3.ca-central-1.amazonaws.com/...",
  "s3_pdf_url": "https://campaign-outputs.s3.ca-central-1.amazonaws.com/...",
  "s3_artifacts_url": "https://campaign-outputs.s3.ca-central-1.amazonaws.com/...",
  "s3_metadata_url": "https://campaign-outputs.s3.ca-central-1.amazonaws.com/...",
  "campaign_brief": {...},
  "final_state": {...},
  "progress_log": {...},
  "agent_interactions": [...]
}
```

### **Global Secondary Indexes**
1. **user_campaigns_index**: Query campaigns by user
2. **status_created_index**: Query campaigns by status and creation time

## ⚙️ **Configuration**

### **Environment Variables (.env)**
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=ca-central-1
AWS_DEFAULT_REGION=ca-central-1

# S3 Configuration
S3_BUCKET_NAME=outputs
S3_BUCKET_REGION=ca-central-1

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=campaigns
DYNAMODB_REGION=ca-central-1
```

### **Required AWS Permissions**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::campaign-outputs",
        "arn:aws:s3:::campaign-outputs/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:ca-central-1:*:table/campaigns",
        "arn:aws:dynamodb:ca-central-1:*:table/campaigns/index/*"
      ]
    }
  ]
}
```

## 🚀 **API Endpoints**

### **1. Get Campaign AWS Info**
```http
GET /api/v1/campaigns/{campaign_id}/aws
Authorization: Bearer {token}
```

**Response:**
```json
{
  "campaign_id": "campaign_123",
  "aws_services": {
    "s3": {
      "bucket_name": "outputs",
      "region": "ca-central-1",
      "files": {
        "website": "https://campaign-outputs.s3.ca-central-1.amazonaws.com/...",
        "pdf": "https://campaign-outputs.s3.ca-central-1.amazonaws.com/...",
        "artifacts": "https://campaign-outputs.s3.ca-central-1.amazonaws.com/...",
        "metadata": "https://campaign-outputs.s3.ca-central-1.amazonaws.com/..."
      }
    },
    "dynamodb": {
      "table_name": "campaigns",
      "region": "ca-central-1",
      "data": {...}
    }
  }
}
```

### **2. List AWS Campaigns**
```http
GET /api/v1/campaigns/aws/list
Authorization: Bearer {token}
```

**Response:**
```json
{
  "campaigns": [
    {
      "campaign_id": "campaign_123",
      "campaign_name": "Product Launch",
      "status": "completed",
      "s3_urls": {...}
    }
  ],
  "total": 1,
  "user_id": "username"
}
```

### **3. Get AWS Campaign Stats**
```http
GET /api/v1/campaigns/aws/stats
Authorization: Bearer {token}  # Admin only
```

**Response:**
```json
{
  "aws_stats": {
    "total_campaigns": 25,
    "status_counts": {
      "completed": 20,
      "running": 3,
      "failed": 2
    },
    "completed_campaigns": 20,
    "average_execution_time": 198.5,
    "total_execution_time": 3970.0
  }
}
```

### **4. Delete Campaign from AWS**
```http
DELETE /api/v1/campaigns/{campaign_id}/aws
Authorization: Bearer {token}
```

**Response:**
```json
{
  "campaign_id": "campaign_123",
  "deletion_results": {
    "s3": {"success": true},
    "dynamodb": {"success": true}
  },
  "message": "Campaign deletion completed"
}
```

## 🔧 **Setup Instructions**

### **1. Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **2. Configure AWS Credentials**
```bash
# Option A: Environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Option B: .env file
cp env.example .env
# Edit .env with your AWS credentials
```

### **3. Create S3 Bucket (Optional)**
The system will automatically create the `outputs` bucket if it doesn't exist.

### **4. Create DynamoDB Table (Optional)**
The system will automatically create the `campaigns` table with proper schema if it doesn't exist.

### **5. Start the Backend**
```bash
python -m api.main
```

## 📊 **Automatic Storage Process**

### **Campaign Completion Flow**
1. **Workflow Execution**: AI agents generate campaign content
2. **Local File Generation**: Website HTML and PDF created locally
3. **S3 Upload**: All files automatically uploaded to S3
4. **Metadata Storage**: Campaign metadata stored in DynamoDB
5. **URL Generation**: S3 URLs added to campaign results

### **Storage Triggers**
- **Website Generation**: HTML content uploaded to S3
- **PDF Creation**: PDF file uploaded to S3
- **Workflow Completion**: Final state and artifacts uploaded
- **Metadata Collection**: Progress logs and interactions stored

## 🔍 **Monitoring and Debugging**

### **AWS Service Status**
```bash
# Check AWS configuration
curl http://localhost:8000/api/v1/health

# Check specific campaign AWS info
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/v1/campaigns/{campaign_id}/aws
```

### **Common Issues**
1. **Missing Credentials**: Check `.env` file and AWS credentials
2. **Bucket Permissions**: Ensure S3 bucket permissions are correct
3. **Table Permissions**: Verify DynamoDB table access permissions
4. **Region Mismatch**: Ensure all services use the same AWS region

### **Logs and Debugging**
```bash
# Backend logs show AWS operations
tail -f backend.log | grep -E "(S3|DynamoDB|AWS)"

# Check S3 bucket contents
aws s3 ls s3://outputs/campaigns/ --recursive

# Check DynamoDB table
aws dynamodb scan --table-name campaigns --region ca-central-1
```

## 💰 **Cost Considerations**

### **S3 Costs (Canada Central)**
- **Storage**: $0.023 per GB per month
- **Requests**: $0.0004 per 1,000 GET requests
- **Data Transfer**: $0.09 per GB (outbound)

### **DynamoDB Costs (Canada Central)**
- **Storage**: $0.25 per GB per month
- **Read/Write**: Pay-per-request pricing
- **Estimated**: ~$0.50 per month for 1000 campaigns

### **Cost Optimization**
- **Lifecycle Policies**: Automatically delete old campaigns
- **Compression**: Compress artifacts before storage
- **Cleanup**: Regular cleanup of completed campaigns

## 🔮 **Future Enhancements**

### **Planned Features**
- **CDN Integration**: CloudFront for faster website access
- **Backup Strategy**: Cross-region replication for disaster recovery
- **Analytics**: CloudWatch metrics and dashboards
- **Automation**: Lambda functions for post-processing
- **Multi-tenant**: Separate buckets per organization

### **Advanced Storage Options**
- **Glacier**: Long-term archival of old campaigns
- **Intelligent Tiering**: Automatic cost optimization
- **Encryption**: Server-side encryption for sensitive data
- **Versioning**: Campaign version history and rollbacks

## 📚 **Additional Resources**

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [boto3 Python SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) 