from aws_cdk import (
    aws_ec2 as ec2,
    aws_s3 as s3,
    core
)


class VpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        subnet_config = [
            {
                'subnetType': ec2.SubnetType.PUBLIC,
                'name': 'public-subnet',
                'cidrMask': 24
            },
            {
                'subnetType': ec2.SubnetType.PRIVATE,
                'name': 'private-subnet',
                'cidrMask': 24
            }
        ]

        vpc = ec2.Vpc(self,
                      "vpc-data-eng-cdk",
                      cidr='10.0.0.0/20',
                      max_azs=2,
                      subnet_configuration=subnet_config)

        bucket = s3.Bucket(
            self, "artifact-bucket-data-eng-cdk",
            bucket_name="artifact-bucket-data-eng-cdk",
            versioned=True,
            removal_policy=core.RemovalPolicy.DESTROY)

        self.output_props = {'bucket': bucket}

    @property
    def outputs(self):
        return self.output_props







