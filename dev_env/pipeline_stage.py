from constructs import Construct
from aws_cdk import Stage
from .DevEnv_stack import DevEnvStack


class PipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = DevEnvStack(self, "Dev-Environment")
