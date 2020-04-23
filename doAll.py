import boto3
from sagemaker import get_execution_role
#currently doesnt loads model to s3,
sm_client = boto3.client(service_name='sagemaker')
runtime_sm_client = boto3.client(service_name='sagemaker-runtime')
projectname = 'omri-model'
account_id = boto3.client('sts').get_caller_identity()['Account']
region = boto3.Session().region_name

bucket = 'sagemaker-{}-{}'.format(region, account_id)
prefix = projectname + '-multimodel-endpoint'

role = 'arn:aws:iam::670666783087:role/service-role/AmazonSageMaker-ExecutionRole-20200331T124902'

from time import gmtime, strftime

model_name = projectname + '-MMS-Model' + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
model_url = 'https://s3-{}.amazonaws.com/{}/{}/'.format(region, bucket, prefix)
container = '{}.dkr.ecr.{}.amazonaws.com/{}:latest'.format(account_id, region, 'sagemaker-' + projectname) #algorithm_name = 'sagemaker-' + projectname

print('Model name: ' + model_name)
print('Model data Url: ' + model_url)
print('Container image: ' + container)

container = {
    'Image': container,
    'ModelDataUrl': model_url,
    'Mode': 'MultiModel'
}

create_model_response = sm_client.create_model(
    ModelName = model_name,
    ExecutionRoleArn = role,
    Containers = [container])

print("Model Arn: " + create_model_response['ModelArn'])


endpoint_config_name = projectname + '-MultiModelEndpointConfig-' + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
print('Endpoint config name: ' + endpoint_config_name)

create_endpoint_config_response = sm_client.create_endpoint_config(
    EndpointConfigName = endpoint_config_name,
    ProductionVariants=[{
        'InstanceType': 'ml.m5.xlarge',
        'InitialInstanceCount': 2,
        'InitialVariantWeight': 1,
        'ModelName': model_name,
        'VariantName': 'AllTraffic'}])

print("Endpoint config Arn: " + create_endpoint_config_response['EndpointConfigArn'])
#
import time

endpoint_name = projectname + '-MultiModelEndpoint-' + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
print('Endpoint name: ' + endpoint_name)

create_endpoint_response = sm_client.create_endpoint(
    EndpointName=endpoint_name,
    EndpointConfigName=endpoint_config_name)
print('Endpoint Arn: ' + create_endpoint_response['EndpointArn'])

resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
status = resp['EndpointStatus']
print("Endpoint Status: " + status)

print('Waiting for {} endpoint to be in service...'.format(endpoint_name))
waiter = sm_client.get_waiter('endpoint_in_service')
waiter.wait(EndpointName=endpoint_name)