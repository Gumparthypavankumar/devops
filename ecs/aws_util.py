import boto3

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