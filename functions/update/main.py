import boto3
import json
import os

client = boto3.client('route53')

def lambda_handler(event, context):
    params = event['queryStringParameters']
    # get IP from query string
    ip = params.get('ip')
    if not ip:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "IP is required"})
        }

    # get name from query string
    name = params.get('domain')
    if not name:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Name is required"})
        }

    # Get the hosted zone ID from env variable
    hosted_zone_id = os.environ['HOSTED_ZONE_ID']

    # add a new record
    response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Comment': 'Add a new record',
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': name + '.devspaces.online',
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [
                            {
                                'Value': ip
                            },
                        ],
                    }
                },
            ]
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({"address": name + '.devspaces.online'})
    }