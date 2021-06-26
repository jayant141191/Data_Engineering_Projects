from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_cloudformation as cfn,
    aws_ssm as ssm,
    aws_iam as iam,
    core
)


class PipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        github_user = ssm.StringParameter.value_from_lookup(
            self,
            parameter_name='/serverless-pipeline/codepipeline/github/user')

        github_repo = ssm.StringParameter.value_from_lookup(
            self,
            parameter_name='/serverless-pipeline/codepipeline/github/repo')

        github_token = core.SecretValue.secrets_manager(
           '/serverless-pipeline/secrets/github/token_1',
           json_field='github-token')

        code_build_role_arn = 'arn:aws:iam::334394862914:role/code_build_role'

        build_project = codebuild.PipelineProject(self,
                                                  'vpc-stack-de-cdk-codebuild',
                                                  project_name='vpc-stack-de-cdk-codebuild',
                                                  description='VPC stack creation using CDK and CodeBuild',
                                                  environment=codebuild.LinuxBuildImage.STANDARD_2_0,
                                                  build_spec=codebuild.BuildSpec.from_source_filename(
                                                      filename='buildspec.yml'
                                                  ),
                                                  role=iam.Role.from_role_arn(self, 'role-id-1', code_build_role_arn),
                                                  timeout=core.Duration.minutes(60))

        props['bucket'].grant_read_write(build_project)

        code_pipeline_role_arn = 'arn:aws:iam::334394862914:role/code_pipeline_role'

        pipeline = codepipeline.Pipeline(self,
                                         'vpc-stack-de-cdk-pipeline',
                                         pipeline_name='vpc-stack-de-cdk-pipeline',
                                         artifact_bucket=props['bucket'],
                                         role=iam.Role.from_role_arn(self, 'role-id-2', code_pipeline_role_arn))

        props['bucket'].grant_read_write(pipeline.role)

        source_output = codepipeline.Artifact()
        pipeline.add_stage(stage_name='Source',
                           actions=[
                               codepipeline_actions.GitHubSourceAction(
                                   action_name='GitHub',
                                   owner=github_user,
                                   repo=github_repo,
                                   branch='master',
                                   oauth_token=github_token,
                                   output=source_output)
                           ])

        build_output = codepipeline.Artifact()
        pipeline.add_stage(stage_name='Build',
                           actions=[
                               codepipeline_actions.CodeBuildAction(
                                   action_name='CodeBuild',
                                   input=source_output,
                                   outputs=[build_output],
                                   project=build_project,
                                   type=codepipeline_actions.CodeBuildActionType.BUILD,
                                   role=iam.Role.from_role_arn(self, 'role-id-3', code_build_role_arn))
                           ])

        cloudformation_role_arn = 'arn:aws:iam::334394862914:role/cloudformation_role'

        cfn_output = codepipeline.Artifact()
        pipeline.add_stage(stage_name='Staging',
                           actions=[
                               codepipeline_actions.CloudFormationCreateUpdateStackAction(
                                   action_name='DeployStack',
                                   admin_permissions=True,
                                   stack_name='vpc-stack-de-cdk-stg',
                                   template_path=codepipeline.ArtifactPath(
                                       build_output,
                                       file_name='vpc-stack-de-cdk-stg.template.json'),
                                   capabilities=[cfn.CloudFormationCapabilities.ANONYMOUS_IAM],
                                   output=cfn_output,
                                   output_file_name='cfn_output',
                                   deployment_role=iam.Role.from_role_arn(self, 'role-id-4', cloudformation_role_arn),
                                   role=iam.Role.from_role_arn(self, 'role-id-5', cloudformation_role_arn))
                           ])

        core.CfnOutput(
            self, 'BuildArtifactsBucketOutput',
            value=props['bucket'].bucket_name,
            description='Amazon S3 Bucket for Pipeline and Build artifacts')

        core.CfnOutput(
            self, 'CodeBuildProjectOutput',
            value=build_project.project_arn,
            description='CodeBuild Project name')

        core.CfnOutput(
            self, 'CodePipelineOutput',
            value=pipeline.pipeline_arn,
            description='AWS CodePipeline pipeline name')
