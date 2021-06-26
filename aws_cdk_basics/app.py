from aws_cdk import core

from cafu_vpc_stack.vpc_stack import VpcStack
from cafu_vpc_stack.pipeline_stack import PipelineStack

app = core.App()
vpc_stack = VpcStack(app, 'vpc-stack-de-cdk-stg', env={'account': '334394862914', 'region': 'us-west-2'})
code_pipeline_stack = PipelineStack(app, 'pipeline-stack-de-cdk-stg', vpc_stack.outputs, env={'account': '334394862914', 'region': 'us-west-2'})

# code_pipeline_stack.add_dependency(vpc_stack)
app.synth()
