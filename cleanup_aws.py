import json
from pathlib import Path
import boto3
cfg=json.loads(Path('generated/demo-config.json').read_text())
region,bucket,secret=cfg['region'],cfg['bucket'],cfg['secret_name']
s3=boto3.client('s3',region_name=region); sm=boto3.client('secretsmanager',region_name=region)
try:
    r=s3.list_objects_v2(Bucket=bucket)
    for o in r.get('Contents',[]): s3.delete_object(Bucket=bucket,Key=o['Key'])
    s3.delete_bucket(Bucket=bucket); print('Deleted bucket',bucket)
except Exception as e: print('Bucket cleanup:',e)
try:
    sm.delete_secret(SecretId=secret,ForceDeleteWithoutRecovery=True); print('Deleted secret',secret)
except Exception as e: print('Secret cleanup:',e)
