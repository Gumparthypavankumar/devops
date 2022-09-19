import boto3
import enum
from botocore import client as BotoClient
from botocore.exceptions import ClientError
import os
import json


class Profile(enum.Enum):
    PROD = 'prod'
    UAT = 'uat'
    DEV = 'dev'


# Constants
PARAMETER_ENVIRONMENT = 'Staging-1.0.0'  # This is used as tag while creating parameter
ACCOUNT_OWNER = 'Owner'
COST_CENTER = 'Cost Owner'
PARAMETER_NAME_PREFIX = '/stage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_ACCESS_SECRET_KEY = os.getenv('AWS_ACCESS_SECRET_KEY')
ACTIVE_PROFILE = Profile.UAT.value


class ParamType(enum.Enum):
    String = 'String'
    SecureString = 'SecureString'


def get_absolute_path_of_file(file_name: str):
    """
        :param -> file_name
        :return -> file_path
        :desc -> Generate absolute path for a file name
    """
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return '/'.join([curr_dir, file_name])


def fetch_client(client: str = 'ssm') -> BotoClient:
    """
        :param -> client name
        :return -> Boto ssm client
        :desc -> Get Aws client using boto3
    """
    if AWS_ACCESS_KEY_ID is None or AWS_ACCESS_SECRET_KEY is None:
        raise ValueError(f"Please Provide access and secret key as env variables to connect to aws client")
    boto_client = boto3.client(client, aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_ACCESS_SECRET_KEY)
    return boto_client


def create_parameter(ssm_client: BotoClient, name: str, value: str, desc: str, param_type: ParamType = ParamType.String,
                     over_write=False) -> None:
    """
        :param -> self explanatory
        :return -> None
        :desc -> This is responsible to create a parameter in ssm store
                    Two things to consider here:
                        1. If parameter exist, an exception is raised if you don't want this behaviour pass in over_write as True
                        2. Name, value and desc should not be empty
    """
    try:
        if value == "" or name == "" or desc == "":
            raise ValueError(f"Name, value and description cannot be empty. Data passed {name}, {value}, {desc}")
        ssm_client.put_parameter(
            Name="/".join([PARAMETER_NAME_PREFIX, name]),
            Value=value,
            Description=desc,
            Type=param_type.value,
            DataType='text',
            Tier='Standard',
            Overwrite=over_write,
            Tags=[
                {
                    'Key': 'CostCenter',
                    'Value': COST_CENTER
                },
                {
                    'Key': 'Owner',
                    'Value': ACCOUNT_OWNER
                },
                {
                    'Key': 'Environment',
                    'Value': PARAMETER_ENVIRONMENT
                }
            ]
        )
    except ssm_client.exceptions.ParameterAlreadyExists as pe:
        raise pe
    except ClientError as ce:
        print(f"Failed to create parameter with message : {str(ce)}")


def get_parameter(ssm_client: BotoClient, parameter_name: str):
    """
        :param -> self explanatory
        :desc -> Get ssm parameter for an client filtered by parameter name
    """
    try:
        parameter = ssm_client.get_parameter(Name=parameter_name)
        return parameter
    except ssm_client.exceptions.ParameterNotFound as pf:
        print(f"Parameter with name {parameter_name} is not found")
    except ClientError as ex:
        print(f"Failed to fetch parameter with message : {str(ex)}")


def get_parameters(ssm_client: BotoClient, params: [{}]):
    """
        :param -> self explanatory
        :desc -> Get a group of ssm parameters for a client
    """
    try:
        names = []
        for param in params:
            names.append('/'.join([PARAMETER_NAME_PREFIX, param['name']]))
        fetched_params = ssm_client.get_parameters(Names=names)
        return fetched_params['Parameters']
    except ssm_client.exceptions.InternalServerError as ex:
        print(f"Failed to fetch parameters with message : {str(ex)}")
    except ClientError as cex:
        print(f"Failed to fetch parameter with message : {str(cex)}")


def construct_parameter_arn(aws_client: BotoClient, parameters: [dict]) -> [dict]:
    """
        :param -> self explanatory
        @desc -> Construct a payload with key value pairs having key as name of parameter and value as arn reference
                    Two things to consider here
                    1. Limitation of get_parameters in boto client. The instance only allows 10 params to pull at a time. so we used slicing to fetch records some at a
                        time and continue to do it until we get all and arrange it in some object
                    2. we want to have key as just the name not as a defined path soo we just take out some prefix out of it which was added
    """
    length: int = len(parameters)
    prefix_length: int = len(PARAMETER_NAME_PREFIX)
    resource_names: [dict] = []
    try:
        start_index = 0
        while start_index < length:  # BotoClient get_parameters doesn't allow to pull values more than 10
            end_index = start_index + 10  # Fetch 10 records at a time
            params = get_parameters(aws_client,
                                    parameters[start_index:end_index])  # slicing/ paginate 10 records at once
            for p in params:
                resource_names.append({
                    'name': p['Name'][prefix_length + 1:],
                    'valueFrom': p['ARN'],
                })
            start_index += 10
        return resource_names
    except KeyError as ex:
        print(f'Key not found with message : {str(ex)}')


def write_arn_params_to_file(arn_params: [dict]) -> None:
    """
        :param -> self explanatory
        :desc -> write a arn param to a json file
    """
    system_arn_parameters_file = get_absolute_path_of_file(f'json-files/system_arn_parameters_{ACTIVE_PROFILE}.json')
    json_data = json.dumps(arn_params, indent=4)
    with open(system_arn_parameters_file, 'w') as outfile:
        outfile.write(json_data)


def add_parameters(aws_client: BotoClient, parameters: [dict]):
    """
        :param -> self explanatory
        :desc -> Add group of parameters into parameter store
    """
    failed_params: [{}] = []
    failed_count = 0
    for parameter in parameters:
        param_type: ParamType = ParamType.SecureString if parameter['isSecure'] else ParamType.String
        try:
            create_parameter(ssm_client=aws_client, name=parameter['name'], value=parameter['value'],
                             desc=parameter['description'], param_type=param_type, over_write=False)
        except (aws_client.exceptions.ParameterAlreadyExists, ValueError) as ex:
            failed_params.append({'name': parameter['name'], 'message': str(ex)})
            failed_count += 1
            pass
    if failed_count > 0:
        print(
            f"Failed to add {failed_count} params. if you want to override set the property in create_parameter over_write to True")
        print(f"failed params are : {failed_params}")


def mask_input(raw_input: str, not_mask_char_count: int = 4) -> str:
    """
        :param -> self explanatory
        :desc -> This is used to mask input and show on the console. Expect the not masking count chars
    """
    length = len(raw_input)
    new_str = ''
    if length <= 4:
        return new_str
    for char in range(0, length - not_mask_char_count):
        new_str += '*'
    return ''.join([new_str, raw_input[length - not_mask_char_count: length]])


if __name__ == "__main__":
    try:
        aws_client = fetch_client()
        print(f"Access Key : {mask_input(AWS_ACCESS_KEY_ID)}")
        print(f"Secret Key : {mask_input(AWS_ACCESS_SECRET_KEY)}")
        print(f"Account Owner : {ACCOUNT_OWNER}")
        print(f"CostCenter : {COST_CENTER}")
        print(f"Parameter Environment : {PARAMETER_ENVIRONMENT}")
        print(f"Parameter Name Prefix : {PARAMETER_NAME_PREFIX}")
        print(f"Active Profile : {ACTIVE_PROFILE}")
        confirmation_log = str(input("Is above configuration ok? Confirm with Yes/ No : ")).strip()
        while True:
            if confirmation_log != 'Yes' and confirmation_log != 'No':
                confirmation_log = str(input("Only Yes/ No are allowed : ")).strip()
            else:
                break
        if confirmation_log == 'Yes':
            print('---------------Processing-------------------------\n')
            # Load file data
            # TODO: Throws error check file before running script
            system_parameters_file = get_absolute_path_of_file(f'json-files/system_parameters_{ACTIVE_PROFILE}.json')
            with open(system_parameters_file) as file_data:
                env_properties = json.loads(file_data.read())
                try:
                    parameters = env_properties['parameters']
                    # Uncomment below
                    add_parameters(aws_client, parameters)
                    resource_names = construct_parameter_arn(aws_client, parameters)
                    write_arn_params_to_file(resource_names)
                except KeyError as ke:
                    print(f"Key not found with message : {str(ke)}")
        else:
            print("Exiting... Since replied with No")
            exit(0)
    except (ClientError, ValueError) as e:
        print(f"Data is invalid with message : {str(e)}")
