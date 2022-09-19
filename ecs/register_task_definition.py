import os
import json
from botocore import client as BotoClient
from botocore.exceptions import ClientError

from ssm_parameter_script import fetch_client, mask_input

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_ACCESS_SECRET_KEY = os.getenv('AWS_ACCESS_SECRET_KEY')
ECS_TASK_DEFINITION_FAMILY = ''
ECS_TASK_ROLE_ARN = ''
ECS_TASK_EXECUTION_ROLE_ARN = ''
CONTAINER_NAME = ''
CONTAINER_IMAGE_URI = ''


def get_absolute_path_of_file(file_name: str):
    """
        :param -> file_name
        :desc -> Generate absolute path for a file name
    """
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return '/'.join([curr_dir, file_name])


def register_task_definition(ecs_client: BotoClient, env_json_file_path: str) -> None:
    """
        :param env_json_file_path:
        :param ecs_client:
        :return -> None
        :desc -> Creates a new revision for task definition with environment file taken as json
    """
    system_parameters_file = get_absolute_path_of_file(env_json_file_path)
    with open(system_parameters_file) as file_data:
        env_properties = json.loads(file_data.read())
        ecs_client.register_task_definition(
            family=ECS_TASK_DEFINITION_FAMILY,
            taskRoleArn=ECS_TASK_ROLE_ARN,
            executionRoleArn=ECS_TASK_EXECUTION_ROLE_ARN,
            networkMode='awsvpc',
            requiresCompatibilities=[
                'FARGATE'
            ],
            cpu='1024',  # 1 vCPU
            memory='4096',  # 4GB
            containerDefinitions=[
                {
                    'name': CONTAINER_NAME,
                    'image': CONTAINER_IMAGE_URI,
                    'portMappings': [
                        {
                            'containerPort': 8080,
                            'protocol': 'tcp'
                        },
                    ],
                    'secrets': env_properties,
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': '/ecs/dev-1-0-0-ecs-td-backend',
                            'awslogs-region': 'ap-south-1',
                            'awslogs-stream-prefix': 'ecs'
                        }
                    },
                },
            ],
        )


if __name__ == '__main__':
    try:
        aws_client = fetch_client('ecs')
        print(f"Access Key : {mask_input(AWS_ACCESS_KEY_ID)}")
        print(f"Secret Key : {mask_input(AWS_ACCESS_SECRET_KEY)}")
        print(f"Ecs task definition : {ECS_TASK_DEFINITION_FAMILY}")
        print(f"Ecs task role arn : {ECS_TASK_ROLE_ARN}")
        print(f"Ecs task execution role arn : {ECS_TASK_EXECUTION_ROLE_ARN}")
        print(f"Container Name : {CONTAINER_NAME}")
        print(f"Container URI : {CONTAINER_IMAGE_URI}")
        confirmation_log = str(input("Is above configuration ok? Confirm with Yes/ No : ")).strip()
        while True:
            if confirmation_log != 'Yes' and confirmation_log != 'No':
                confirmation_log = str(input("Only Yes/ No are allowed : ")).strip()
            else:
                break
        if confirmation_log == 'Yes':
            print('---------------Processing-------------------------\n')
            register_task_definition(fetch_client('ecs'), 'json-files/system_arn_parameters.json')
        else:
            print("Exiting... Since replied with No")
            exit(0)
    except (ClientError, ValueError) as e:
        print(f"Data is invalid with message : {str(e)}")

