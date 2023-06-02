from constructs import Construct
from aws_cdk import Stage
from .ec2_stack import Ec2Stack


class PipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = Ec2Stack(self, "Dev-Environment")
