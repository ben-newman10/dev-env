from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    Tags,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
)


class DevInstance(Construct):
    @property
    def vpc(self):
        return self._vpc

    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.Vpc,
        secret_arn: secretsmanager.Secret.secret_arn,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        # Create the EC2 instance role with SSM permissions
        instance_role = iam.Role(
            self,
            "DevInstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                )
            ],
        )

        # Add permissions to the role to access the Secret
        instance_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["secretsmanager:GetSecretValue"],
                resources=[secret_arn],
            )
        )

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
            role=instance_role,
        )

        # Add tags to the EC2
        Tags.of(instance).add("Name", id)
        Tags.of(instance).add("autoshutdown", "true")
