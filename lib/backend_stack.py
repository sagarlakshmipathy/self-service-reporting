import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    Stack
)
from constructs import Construct

class BackendStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # import the cognito user pool client id from AuthenticationStack
        user_pool_client_id = cdk.Fn.import_value('UserPoolClientId')
        
        # import the cognito user pool domain from AuthenticationStack
        domain_name = cdk.Fn.import_value('UserPoolDomainUrl')

        # create a role and policy for the lambda function
        lambda_iam_role = iam.Role(
            self, 'LambdaSelfServiceReportingRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            )
        
        iam.ManagedPolicy(
            self, 'LambdaSelfServiceReportingPolicy',
            managed_policy_name='LambdaSelfServiceReportingPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        'quicksight:*',
                        'logs:*'
                        ],
                    resources=['*']
                    )
                ],
            roles=[lambda_iam_role]
            )
        
        # define the lambda functions
        self_service_reporting = _lambda.Function(
            self, 'SelfServiceReportingFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            function_name='self-service-reporting-function',
            code=_lambda.Code.from_asset('./app/self-service-reporting'),
            handler='lambda_function.lambda_handler',
            role=lambda_iam_role,
            timeout=cdk.Duration.minutes(1),
            environment={
                'CognitoClientId': user_pool_client_id,
                'CognitoDomainUrl': f"https://{domain_name}.auth.us-east-1.amazoncognito.com"
                }
            )
        
        # create the API Gateway
        api = apigw.RestApi(
            self, 'ApiGateway',
            rest_api_name='self-service-reporting-api',
            description='This is the gateway to create the self service reports in QuickSight',
            deploy_options={
                'stage_name': 'Dev'
                },
            )
        
        # add analysis merge resource to the API Gateway
        analysis_merge_resource = api.root.add_resource('qs-self-service-reporting-api')
        
        # add the GET method to the analysis merge resource
        analysis_get_method = analysis_merge_resource.add_method(
            'GET',
            apigw.LambdaIntegration(
                self_service_reporting,
                proxy=True,
                allow_test_invoke=False,
                integration_responses=[
                    apigw.IntegrationResponse(
                        status_code='200',
                        response_templates={
                            'application/json': 'Empty'
                            },
                        response_parameters={
                            'method.response.header.Access-Control-Allow-Origin': "'*'"
                            }
                        )
                    ]
                ),
            )
        
        analysis_get_method.add_method_response(
            status_code='200',
            response_models={
                'application/json': apigw.Model.EMPTY_MODEL
                },
            response_parameters={
                'method.response.header.Access-Control-Allow-Origin': True,
                }
            )
        
        # export the API Gateway URL
        cdk.CfnOutput(
            self, 'ApiGatewayUrl',
            value=api.url,
            export_name='ApiGatewayUrl'
            )