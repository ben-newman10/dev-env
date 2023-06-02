#!/usr/bin/env python3
import os

import aws_cdk as cdk

from dev_env.pipeline_stack import PipelineStack


app = cdk.App()
PipelineStack(app, "DevEnvStack")

app.synth()
