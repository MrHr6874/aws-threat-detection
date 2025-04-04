# AWS Threat Detection Project
This project detects unusual activity in AWS logs using Python and AWS Lambda.

## Overview
The goal is to monitor AWS CloudWatch logs for unusual activity (such as multiple failed login attempts) and trigger alerts via SNS notifications.

## Services Used
- **AWS Lambda**: Serverless compute to execute the threat detection script.
- **Amazon CloudWatch**: Logs AWS activity and triggers alerts.
- **Amazon SNS (Simple Notification Service)**: Sends alerts via email or SMS.
- **AWS IAM (Identity and Access Management)**: Controls access permissions for Lambda and other AWS services.

## Why These Services?
- **AWS Lambda** eliminates the need for dedicated infrastructure, reducing cost and maintenance.
- **CloudWatch** allows real-time monitoring of AWS logs for security events.
- **SNS** ensures prompt alerts are sent to administrators upon detecting a potential security breach.
- **IAM** ensures least-privilege access for secure and controlled execution of Lambda functions.

---

## Setup Instructions
### 1. Clone the Repository
```sh
git clone https://github.com/YOUR_GITHUB_USERNAME/aws-threat-detection.git
cd aws-threat-detection
```

### 2. Create an SNS Topic and Subscription
```sh
aws sns create-topic --name ThreatAlerts
aws sns subscribe --topic-arn arn:aws:sns:YOUR_REGION:YOUR_ACCOUNT_ID:ThreatAlerts --protocol email --notification-endpoint your-email@example.com
```
Confirm the email subscription before proceeding.

### 3. Create an IAM Role for Lambda
Create a trust policy (`trust-policy.json`):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```
Create the IAM role:
```sh
aws iam create-role --role-name LambdaThreatDetectionRole \
    --assume-role-policy-document file://trust-policy.json
```
Attach permissions for CloudWatch and SNS:
```sh
aws iam attach-role-policy --role-name LambdaThreatDetectionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam attach-role-policy --role-name LambdaThreatDetectionRole \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess
aws iam attach-role-policy --role-name LambdaThreatDetectionRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess
```

### 4. Deploy the Lambda Function
Create a Python script (`lambda_function.py`):
```python
import json
import boto3

def lambda_handler(event, context):
    sns_client = boto3.client('sns')
    message = "Potential security threat detected in AWS logs!"
    sns_client.publish(TopicArn='arn:aws:sns:YOUR_REGION:YOUR_ACCOUNT_ID:ThreatAlerts', Message=message)
    return {
        'statusCode': 200,
        'body': json.dumps('Alert Sent!')
    }
```
Package the function:
```sh
zip function.zip lambda_function.py
```
Create the Lambda function:
```sh
aws lambda create-function --function-name ThreatDetectionLambda \
    --runtime python3.8 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/LambdaThreatDetectionRole \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip
```

### 5. Set Up a CloudWatch Rule
Create a rule to trigger Lambda on failed login attempts:
```sh
aws events put-rule --name FailedLoginAttempts --event-pattern '{"source":["aws.cloudtrail"], "detail-type":["AWS API Call via CloudTrail"], "detail":{"eventName":["ConsoleLogin"], "errorMessage":["Failed authentication"]}}'
```
Attach the Lambda function as a target:
```sh
aws events put-targets --rule FailedLoginAttempts --targets "Id"="1","Arn"="arn:aws:lambda:YOUR_REGION:YOUR_ACCOUNT_ID:function:ThreatDetectionLambda"
```
Grant permissions for EventBridge to invoke Lambda:
```sh
aws lambda add-permission --function-name ThreatDetectionLambda \
    --statement-id EventBridgeInvoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:YOUR_REGION:YOUR_ACCOUNT_ID:rule/FailedLoginAttempts
```

### 6. Test the Lambda Function
Manually trigger the function to verify alerts:
```sh
aws lambda invoke --function-name ThreatDetectionLambda output.json
cat output.json
```
If everything is set up correctly, you should receive an email alert from SNS.

---

## Cleanup
To prevent incurring charges, delete all resources:
```sh
aws sns delete-topic --topic-arn arn:aws:sns:YOUR_REGION:YOUR_ACCOUNT_ID:ThreatAlerts
aws lambda delete-function --function-name ThreatDetectionLambda
aws iam delete-role --role-name LambdaThreatDetectionRole
aws events delete-rule --name FailedLoginAttempts
```

---

## Next Steps & Enhancements
1. **Extend Threat Detection**: Analyze logs for multiple failed login attempts over a period instead of single failures.
2. **Auto-Remediation**: Implement an IAM policy to automatically disable compromised users.
3. **Advanced Logging & Storage**: Store logs in S3 for long-term security analysis.
4. **Machine Learning Integration**: Use AI models to detect anomalous behaviors more accurately.
5. **Multi-Channel Alerts**: Extend SNS to support SMS or Slack notifications.
6. **Dashboard & Reporting**: Use AWS QuickSight for visualization of security threats.

