from diagrams import Diagram
from diagrams.aws.storage import S3
from diagrams.aws.network import CloudFront

with Diagram("static-site"):
    cloud_front = CloudFront("distribution")
    s3 = S3("assets")

    cloud_front >> s3
