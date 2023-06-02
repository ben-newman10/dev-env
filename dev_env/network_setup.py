from constructs import Construct
from aws_cdk import aws_ec2 as ec2


class NetworkSetup(Construct):
    @property
    def vpc(self):
        return self._vpc

    def __init__(self, scope: Construct, id: str, **kwargs):
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
        self._vpc = ec2.Vpc(
            self,
            "DevVPC",
            max_azs=1,
            subnet_configuration=[private_subnet, public_subnet],
        )

        # Create an Elastic IP for the Nat Gateway
        eip = ec2.CfnEIP(self, "DevEIP")
        allocation_id = eip.attr_allocation_id

        # Create NAT Gateway
        nat_gateway = ec2.CfnNatGateway(
            self,
            "DevNatGateway",
            subnet_id=self._vpc.public_subnets[0].subnet_id,
            allocation_id=allocation_id,
        )
