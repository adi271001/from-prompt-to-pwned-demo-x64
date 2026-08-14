import json, os
from pathlib import Path
import boto3

REGION = os.getenv('AWS_REGION', 'us-east-1')
sts = boto3.client('sts', region_name=REGION)
ACCOUNT = sts.get_caller_identity()['Account']
BUCKET = f'fp2pwned-demo-{ACCOUNT}'
SECRET_NAME = 'fp2pwned/demo-secret'

s3 = boto3.client('s3', region_name=REGION)
sm = boto3.client('secretsmanager', region_name=REGION)

try:
    s3.head_bucket(Bucket=BUCKET)
except Exception:
    if REGION == 'us-east-1':
        s3.create_bucket(Bucket=BUCKET)
    else:
        s3.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={'LocationConstraint': REGION})

for key, body in {
    'architecture.pdf': b'DEMO FILE - architecture placeholder',
    'deployment.txt': b'DEMO FILE - deployment notes placeholder',
    'README.md': b'DEMO FILE - harmless project README',
}.items():
    s3.put_object(Bucket=BUCKET, Key=key, Body=body)

try:
    sm.create_secret(Name=SECRET_NAME, Description='Fake secret for FROM PROMPT TO PWNED demo', SecretString='DEMO_API_KEY=aws-demo-not-real')
except sm.exceptions.ResourceExistsException:
    sm.put_secret_value(SecretId=SECRET_NAME, SecretString='DEMO_API_KEY=aws-demo-not-real')

policy = {
  'Version':'2012-10-17',
  'Statement':[
    {'Sid':'BedrockInvoke','Effect':'Allow','Action':['bedrock:InvokeModel'],'Resource':'*'},
    {'Sid':'DemoS3Read','Effect':'Allow','Action':['s3:ListBucket'],'Resource':f'arn:aws:s3:::{BUCKET}'},
    {'Sid':'DemoSecretRead','Effect':'Allow','Action':['secretsmanager:GetSecretValue'],'Resource':f'arn:aws:secretsmanager:{REGION}:{ACCOUNT}:secret:{SECRET_NAME}-*'}
  ]
}
Path('generated').mkdir(exist_ok=True)
Path('generated/demo-policy.json').write_text(json.dumps(policy, indent=2))
Path('generated/demo-config.json').write_text(json.dumps({'region':REGION,'bucket':BUCKET,'secret_name':SECRET_NAME,'model_id':'amazon.nova-lite-v1:0'}, indent=2))
print(f'Region: {REGION}\nBucket: {BUCKET}\nSecret: {SECRET_NAME}\nModel: amazon.nova-lite-v1:0')
print('Attach generated/demo-policy.json to the AWS identity running the demo.')
