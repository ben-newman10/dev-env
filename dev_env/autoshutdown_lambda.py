from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    Duration,
    aws_events as events,
    aws_events_targets as targets,
)


class AutoShutdownLambda(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Lambda to auto shutdown instances
        shutdown_lambda = _lambda.Function(
            self,
            "ShutdownLambda",
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
                resources=["*"],
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
        rule.add_target(target=targets.LambdaFunction(handler=shutdown_lambda))
