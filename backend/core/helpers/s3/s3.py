import logging
import os

import boto3
from botocore.exceptions import ClientError

from core.db_config import config


class S3:
    def __init__(self):
        self.bucket = config.AWS_DEFAULT_BUCKET
        self.s3_client = boto3.client(
            service_name='s3',
            region_name=config.AWS_DEFAULT_REGION,
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        )

    async def upload_file(self, file_name, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_name)
        # Upload the file
        try:
            self.s3_client.upload_file(file_name, self.bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True


s3_client = S3()
