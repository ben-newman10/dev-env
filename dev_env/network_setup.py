from constructs import Construct
from aws_cdk import aws_ec2 as ec2


class NetworkSetup(Construct):
    @property
    def vpc(self):
        return self._vpc

    @property
    def security_group(self):
        return self._security_group

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

        # Create a security group
        self._security_group = ec2.SecurityGroup(
            self,
            "DevSG",
            vpc=self._vpc,
        )

        # Create an Elastic IP for the Nat Gateway
        eip = ec2.CfnEIP(self, "DevEIP")
        allocation_id = eip.attr_allocation_id

        # Create NAT Gateway
        ec2.CfnNatGateway(
            self,
            "DevNatGateway",
            subnet_id=self._vpc.public_subnets[0].subnet_id,
            allocation_id=allocation_id,
        )

        # Create GitHub VPC endpoint
        ec2.InterfaceVpcEndpoint(
            self,
            "GitHubEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService(name="github.hosting.com"),
            vpc=self._vpc,
            private_dns_enabled=True,
            security_groups=[self._security_group],
        )

        # Create Bitbucket VPC endpoint
        ec2.InterfaceVpcEndpoint(
            self,
            "BitbucketEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService(name="bitbucket.hosting.com"),
            vpc=self._vpc,
            private_dns_enabled=True,
            security_groups=[self._security_group],
        )
