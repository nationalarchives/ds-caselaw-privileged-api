import environ
import logging

import boto3
import botocore.client
from botocore.exceptions import BotoCoreError

env = environ.Env()


def create_aws_client(service: str):  # service
    """@param: service The AWS service, e.g. 's3'"""
    aws = boto3.session.Session(
        aws_access_key_id=env("AWS_ACCESS_KEY_ID", default=None),
        aws_secret_access_key=env("AWS_SECRET_KEY", default=None),
    )
    return aws.client(
        service,
        endpoint_url=env("AWS_ENDPOINT_URL", default=None),
        region_name=env("PRIVATE_ASSET_BUCKET_REGION", default=None),
        config=botocore.client.Config(signature_version="s3v4"),
    )


def upload_to_invalid_bucket(judgment_uri: str, xml_content: bytes, error_message=None):
    """
    Uploads the XML content to a bucket so its contents can be reviewed.
    """
    bucket = env.get_value("INVALID_XML_BUCKET", default=None)
    if not bucket:
        logging.info(
            "INVALID_XML_BUCKET not set, not uploading XML to S3 for %s", judgment_uri
        )
        return

    client = create_aws_client("s3")
    try:
        client.put_object(
            Body=xml_content,
            Bucket=bucket,
            Key=judgment_uri,
            Metadata={"error": error_message.decode("utf-8", "replace")},
        )
    except BotoCoreError as ex:
        logging.error(ex)
