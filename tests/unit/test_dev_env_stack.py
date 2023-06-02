import aws_cdk as core
import aws_cdk.assertions as assertions

from dev_env.dev_env_stack import DevEnvStack

# example tests. To run these tests, uncomment this file along with the example
# resource in dev_env/dev_env_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DevEnvStack(app, "dev-env")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
