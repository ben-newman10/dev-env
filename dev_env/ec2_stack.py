from aws_cdk import (
    Stack,
    Tags,
    aws_events as events,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_iam as iam,
    Duration,
)
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

        # Lambda to auto shutdown instances
        shutdown_lambda = _lambda.Function(
            self,
            "AutoShutdownLambda",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="autoshutdown.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(30),
            memory_size=256,
        )

        # Add permissions to the Lambda function
        shutdown_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ec2:StopInstances", "ec2:DescribeInstances"],
                resources=["arn:aws:ec2:*:*:instance/*"],
                conditions={"StringEquals": {"ec2:ResourceTag/autoshutdown": "true"}},
            )
        )

        # Create the EventBridge rule to trigget lambda at 7pm every day.
        rule = events.Rule(
            self,
            "MyRule",
            schedule=events.Schedule.cron(
                minute="0", hour="19", month="*", week_day="*", year="*"
            ),
        )

        # Add the Lambda function as a target for the rule
        rule.add_target(shutdown_lambda)
