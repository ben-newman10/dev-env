from aws_cdk import Stack, Tags, aws_ec2 as ec2
from constructs import Construct


class Ec2Stack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Private Subnet
        private_subnet = ec2.SubnetConfiguration(
            name="Private",
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            cidr_mask=24,
        )

        # Create Public Subnet
        public_subnet = ec2.SubnetConfiguration(
            name="Public",
            subnet_type=ec2.SubnetType.PUBLIC,
            cidr_mask=24,
        )

        # Create VPC and add Subnets
        vpc = ec2.Vpc(
            self,
            "DevVPC",
            max_azs=2,
            subnet_configuration=[private_subnet, public_subnet],
        )

        # Create an Elastic IP for the Nat Gateway
        eip = ec2.CfnEIP(self, "DevEIP")
        allocation_id = eip.attr_allocation_id

        # Create NAT Gateway
        nat_gateway = ec2.CfnNatGateway(
            self,
            "DevNatGateway",
            subnet_id=vpc.public_subnets[0].subnet_id,
            allocation_id=allocation_id,
        )

        # Create EC2 Instance
        instance = ec2.Instance(
            self,
            "MyInstance",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            require_imdsv2=True,
            ssm_session_permissions=True,
        )

        Tags.of(instance).add("Name", "BenDev")
        Tags.of(instance).add("autoshutdown", "true")
