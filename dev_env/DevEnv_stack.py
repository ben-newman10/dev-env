from aws_cdk import Stack, aws_secretsmanager as secretsmanager
from constructs import Construct

from dev_env.autoshutdown_lambda import AutoShutdownLambda
from dev_env.network_setup import NetworkSetup
from dev_env.dev_instance import DevInstance


class DevEnvStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Setup Private network with NAT gateway
        network = NetworkSetup(self, "NetworkSetup")

        # Create AWS Secret for setup
        setup_secret = secretsmanager.Secret(
            self,
            "DevSetupSecret",
            secret_name="setup-secret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "admin"}',
                generate_string_key="password",
                password_length=16,
                exclude_punctuation=True,
            ),
        )
        # Get secret value
        # aws secretsmanager get-secret-value --secret-id setup-secret --query SecretString --output text --region eu-west-2

        # Create Dev Instances
        DevInstance(
            self,
            "BenDev",
            vpc=network.vpc,
            secret_arn=setup_secret.secret_arn,
            security_group=network.security_group,
        )
        DevInstance(
            self,
            "TomDev",
            vpc=network.vpc,
            secret_arn=setup_secret.secret_arn,
            security_group=network.security_group,
        )

        # Create autoshutdown lambda (7pm every evening)
        AutoShutdownLambda(self, "AutoShutdownLambda")
