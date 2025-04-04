import boto3
import json

sns_client = boto3.client('sns')
cloudwatch_logs = boto3.client('logs')

SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:532839197548:ThreatAlerts"

def lambda_handler(event, context):
    print("Event Received:", json.dumps(event))

    # Simulated logic: Trigger alert if "Failed login attempt" is detected
    for record in event.get("Records", []):
        if "Failed login attempt" in record.get("message", ""):
            alert_message = f"Alert: Unusual login activity detected! \n\n{record['message']}"
            sns_client.publish(TopicArn=SNS_TOPIC_ARN, Message=alert_message)
            print("Alert sent to SNS")

    return {"statusCode": 200, "body": json.dumps("Execution completed")}
