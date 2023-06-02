from aws_cdk import Stack
from constructs import Construct

from dev_env.autoshutdown_lambda import AutoShutdownLambda
from dev_env.network_setup import NetworkSetup
from dev_env.dev_instance import DevInstance


class DevEnvStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Setup Private network with NAT gateway
        network = NetworkSetup(self, "NetworkSetup")

        # Create Dev Instances
        DevInstance(self, "BenDev", vpc=network.vpc)
        DevInstance(self, "TestDev", vpc=network.vpc)
        DevInstance(self, "TomDev", vpc=network.vpc)

        # Create autoshutdown lambda (7pm every evening)
        shutdown_lambda = AutoShutdownLambda(self, "AutoShutdownLambda")
