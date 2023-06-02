from constructs import Construct
from aws_cdk import aws_ec2 as ec2, Tags


class DevInstance(Construct):
    @property
    def vpc(self):
        return self._vpc

    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create EC2 instance
        instance = ec2.Instance(
            self,
            id,
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            require_imdsv2=True,
            ssm_session_permissions=True,
        )

        # Add tags to the EC2
        Tags.of(instance).add("Name", id)
        Tags.of(instance).add("autoshutdown", "true")
