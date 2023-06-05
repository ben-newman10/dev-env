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
        security_group: ec2.SecurityGroup,
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
            propagate_tags_to_volume_on_creation=True,
            security_group=security_group,
            role=instance_role,
            user_data=ec2.UserData.for_linux(),
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=30,  # Set the root volume to 30GB
                        delete_on_termination=True,  # Delete volume when instance is terminated
                    ),
                )
            ],
        )

        # Add tags to the EC2
        Tags.of(instance).add("Name", id)
        Tags.of(instance).add("autoshutdown", "true")

        # Add user data to the instance
        instance.user_data.add_commands(
            "SECRET=$(aws secretsmanager get-secret-value --secret-id setup-secret --query SecretString --output text --region eu-west-2)",
            "echo $SECRET > /home/ec2-user/setup-secret.txt",
        )

        # Find the volume if it exists
        response = ec2.describe_volumes()
        voluneFound = False

        for volume in response["Volumes"]:
            for tag in volume["Tags"]:
                if tag["Key"] == "Name" and tag["Value"] == "my-volume-name":
                    print(volume["VolumeId"])

        # Create the volume if it doesn't exist
        if not volume:
            volume = ec2.Volume(
                self,
                "Volume",
                size=100,
                availability_zone="eu-west-2a",
                encrypted=True,
            )
        volume_id = voluneFound ? 'hello' : volume_id

        ec2.CfnVolumeAttachment(
            self,
            "MyCfnVolumeAttachment",
            device="device",
            instance_id=instance.instance_id,
            volume_id=volume_id,
        )
