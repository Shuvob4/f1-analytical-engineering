# import necessary libraries
import os
from dotenv import load_dotenv
import boto3

# loading environment variables from the .env file
load_dotenv()

def auth_and_bucket_visibility():
    print('Running Test: Authentication and Bucket Visibility')

    EXPECTED_BUCKETS = [
        'sb-f1-bronze-2024',
        'sb-f1-silver-2024',
        'sb-f1-gold-2024'
    ]
    try:
        # creating connection to s3
        s3_client = boto3.client('s3')

        # getting all the names of the buckets
        response = s3_client.list_buckets()

        # printing all details of the bucket
        for bucket in response['Buckets']:
            print(f"{bucket['Name']} : {bucket['CreationDate']}")
        
        # extracting just bucket names
        bucket_names = [bucket['Name'] for bucket in response['Buckets']]

        # asserting all 3 buckets are present
        for name in EXPECTED_BUCKETS:
            assert name in bucket_names, f'{name} not found in Bucket List.'
        
        print('Authentication and Bucket Visibility Test Passed')
    
    except Exception as e:
        print(f'Authentication and Bucket Visibility Test Failed: {e}')
        raise


def test_round_trip():
    print("Running Test 2 — Write, Read, Delete")

    BRONZE_BUCKET = os.getenv('S3_BRONZE_BUCKET')
    TEST_KEY = 'test/connection_check.txt'
    TEST_CONTENT = 'f1 pipeline connection check'

    step = 'setup'
    try:
        s3_client = boto3.client('s3')

        # Write
        step = 'write'
        s3_client.put_object(
            Bucket=BRONZE_BUCKET,
            Key=TEST_KEY,
            Body=TEST_CONTENT
        )

        # Read
        step = 'read'
        response = s3_client.get_object(
            Bucket=BRONZE_BUCKET,
            Key=TEST_KEY
        )
        content = response['Body'].read().decode('utf-8')  # extract the string from response

        # Assert
        assert content == TEST_CONTENT, f"Content mismatch: expected '{TEST_CONTENT}', got '{content}'"

        # Delete
        step = 'delete'
        s3_client.delete_object(
            Bucket=BRONZE_BUCKET,
            Key=TEST_KEY
        )

        print("Test 2 passed.")

    except Exception as e:
        print(f"Test 2 failed at step [{step}]: {e}")
        raise

if __name__ == "__main__":
    auth_and_bucket_visibility()
    test_round_trip()