from aws_cdk import (
    Stack,
    Tags,
    aws_ec2 as ec2,
)
from constructs import Construct

from dev_env.autoshutdown_lambda import AutoShutdownLambda
from dev_env.network_setup import NetworkSetup


class Ec2Stack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Setup Private network with NAT gateway
        network = NetworkSetup(self, "NetworkSetup")

        # Create EC2 Instance
        instance = ec2.Instance(
            self,
            "BenDevInstance",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=network.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            require_imdsv2=True,
            ssm_session_permissions=True,
        )

        Tags.of(instance).add("Name", "BenDev")
        Tags.of(instance).add("autoshutdown", "true")

        # Create autoshutdown lambda
        shutdown_lambda = AutoShutdownLambda(self, "AutoShutdownLambda")
