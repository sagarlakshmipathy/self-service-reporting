import json, boto3, os, re
import uuid
import urllib.parse

def lambda_handler(event, context):

    # quicksight config
    identity_region = os.environ['REGION']
    qs_client = boto3.client("quicksight", region_name=identity_region)

    if event['queryStringParameters'] is None:
        mode='authenticated'
        print(f"current mode is {mode}")
    elif 'mode' not in event['queryStringParameters'].keys() :
        aws_account_id = urllib.parse.unquote(event['queryStringParameters']['AwsAccountId'])
        source_dashboard_id = urllib.parse.unquote(event['queryStringParameters']['SourceDashboardId'])
        target_analysis_id = urllib.parse.unquote(event['queryStringParameters']['TargetAnalysisId'])
        target_analysis_name = urllib.parse.unquote(event['queryStringParameters']['TargetAnalysisName'])
        target_dashboard_id = urllib.parse.unquote(event['queryStringParameters']['TargetDashboardId'])
        target_dashboard_name = urllib.parse.unquote(event['queryStringParameters']['TargetDashboardName'])
        primary_dimension = urllib.parse.unquote(event['queryStringParameters']['pDimensions'])
        primary_measure = urllib.parse.unquote(event['queryStringParameters']['pMeasures'])
        try:
            secondary_dimensions = event['multiValueQueryStringParameters']['p.pDimensions']
            if secondary_dimensions:
                secondary_dimension_fstring = get_dimension_fstring(secondary_dimensions)
                total_dimensions = get_total_dimensions(primary_dimension, secondary_dimensions)
                dimension_string = '&pDimensions='+primary_dimension+"&"+secondary_dimension_fstring
        except KeyError:
            total_dimensions = primary_dimension
            dimension_string = '&pDimensions='+primary_dimension
        try:
            secondary_measures = event['multiValueQueryStringParameters']['p.pMeasures']
            if secondary_measures:
                secondary_measure_fstring = get_measure_fstring(secondary_measures)
                total_measures = get_total_measures(primary_measure, secondary_measures)
                measure_string = '&pMeasures='+primary_measure+"&"+secondary_measure_fstring
        except KeyError:
            total_measures = primary_measure
            measure_string = '&pMeasures='+primary_measure
        user_name = urllib.parse.unquote(event['queryStringParameters']['UserName'])
        state = 'AwsAccountId='+aws_account_id+'&SourceDashboardId='+source_dashboard_id+'&TargetAnalysisId='+target_analysis_id+'&TargetAnalysisName='+target_analysis_name+'&TargetDashboardId='+target_dashboard_id+'&TargetDashboardName='+target_dashboard_name+'&UserName='+user_name+dimension_string+measure_string
        print(state)
        mode='static'
        print(f"current mode is {mode}")
    elif 'mode' in event['queryStringParameters'].keys():
        mode=event['queryStringParameters']['mode']
        aws_account_id = urllib.parse.unquote(event['queryStringParameters']['AwsAccountId'])
        source_dashboard_id = urllib.parse.unquote(event['queryStringParameters']['SourceDashboardId'])
        target_analysis_id = urllib.parse.unquote(event['queryStringParameters']['TargetAnalysisId'])
        target_analysis_name = urllib.parse.unquote(event['queryStringParameters']['TargetAnalysisName'])
        target_dashboard_id = urllib.parse.unquote(event['queryStringParameters']['TargetDashboardId'])
        target_dashboard_name = urllib.parse.unquote(event['queryStringParameters']['TargetDashboardName'])
        primary_dimension = urllib.parse.unquote(event['queryStringParameters']['pDimensions'])
        primary_measure = urllib.parse.unquote(event['queryStringParameters']['pMeasures'])
        try:
            secondary_dimensions = event['multiValueQueryStringParameters']['p.pDimensions']
            if secondary_dimensions:
                secondary_dimension_fstring = get_dimension_fstring(secondary_dimensions)
                total_dimensions = get_total_dimensions(primary_dimension, secondary_dimensions)
                dimension_string = '&pDimensions='+primary_dimension+"&"+secondary_dimension_fstring
        except KeyError:
            total_dimensions = primary_dimension
            dimension_string = '&pDimensions='+primary_dimension
        try:
            secondary_measures = event['multiValueQueryStringParameters']['p.pMeasures']
            if secondary_measures:
                secondary_measure_fstring = get_measure_fstring(secondary_measures)
                total_measures = get_total_measures(primary_measure, secondary_measures)
                measure_string = '&pMeasures='+primary_measure+"&"+secondary_measure_fstring
        except KeyError:
            total_measures = primary_measure
            measure_string = '&pMeasures='+primary_measure
        user_name = urllib.parse.unquote(event['queryStringParameters']['UserName'])
    print(mode)
    print(f"current mode is {mode}")
    openIdToken = ''
    response={}  
    authEvalMode = 'STS'
    #read environment variables for Cognito Domain and Cognito Client ID
    cognitoDomainUrl = os.environ['CognitoDomainUrl']
    cognitoClientId = os.environ['CognitoClientId']    
    dataset_id = os.environ['DataSetId']
    
    if mode == 'static': 
        htmlFile = open('StaticLoginPage.html', 'r')
        if event['headers'] is None or event['requestContext'] is None:
                apiGatewayUrl = 'ApiGatewayUrlIsNotDerivableWhileTestingFromApiGateway'
        else:
            apiGatewayUrl = 'https://' + event['headers']['Host']+event['requestContext']['path']
        #Read contents of sample html file
        htmlContent = htmlFile.read()
        #Replace place holders.
        htmlContent = re.sub('<cognitoDomainUrl>', cognitoDomainUrl, htmlContent)
        htmlContent = re.sub('<cognitoClientId>', cognitoClientId, htmlContent)
        htmlContent = re.sub('<State>', state, htmlContent)
        #Replace API Gateway url placeholder
        htmlContent = re.sub('<ApiGatewayUrl>', apiGatewayUrl, htmlContent)
        htmlContent = re.sub('<StaticPageUrl>', apiGatewayUrl,htmlContent)
        #Return HTML. 
        return {'statusCode':200,
            'headers': {"Content-Type":"text/html"},
            'body':htmlContent
            }
    elif mode == 'authenticated':
        htmlFile = open('StaticLoginPage.html', 'r')
        if event['headers'] is None or event['requestContext'] is None:
                apiGatewayUrl = 'ApiGatewayUrlIsNotDerivableWhileTestingFromApiGateway'
        else:
            apiGatewayUrl = 'https://' + event['headers']['Host']+event['requestContext']['path']
        #Read contents of sample html file
        htmlContent = htmlFile.read()
        #Replace place holders.
        htmlContent = re.sub('<cognitoDomainUrl>', cognitoDomainUrl, htmlContent)
        htmlContent = re.sub('<cognitoClientId>', cognitoClientId, htmlContent)
        #Replace API Gateway url placeholder
        htmlContent = re.sub('<ApiGatewayUrl>', apiGatewayUrl, htmlContent)
        htmlContent = re.sub('<StaticPageUrl>', apiGatewayUrl,htmlContent)
        #Return HTML. 
        return {'statusCode':200,
            'headers': {"Content-Type":"text/html"},
            'body':htmlContent
            }
    
    elif mode == 'getUrl':
        print('Inside getUrl')

        # first get the dashboard definition from source dashboard
        # use this definition as the base to build the target dashboard
        target_dashboard_definition_initial = get_dashboard_definition(qs_client, aws_account_id, source_dashboard_id)

        # set the dataset identifier declarations in the target dashboard definition
        # use the dataset_id derived from teh environment variables
        target_dashboard_definition_with_dataset = set_dataset_identifier_declarations(qs_client, aws_account_id, target_dashboard_definition_initial, dataset_id)

        # create the table visual skeleton for the target dashboard
        table_visual = create_table_visual()

        # update the table visual with the dimensions and measures for the target dashboard
        # use the dimensions and measures from the user supplied variales from the table generator dashboard
        target_dashboard_definition_with_visual = update_table_visual(total_dimensions, total_measures, target_dashboard_definition_with_dataset, table_visual)

        # delete the target dashboard if it already exists
        # if this is not done, the target dashboard will not be created and the script will fail with ResourceExistsException
        delete_existing_dashboard(aws_account_id, target_dashboard_id, qs_client)

        # publish the dashboard to the account and return to the same page
        # redirection is handled in the html page
        try:
            response = publish_dashboard_to_quicksight(aws_account_id, target_dashboard_id, target_dashboard_name, target_dashboard_definition_with_visual, user_name, qs_client)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(response)
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(e)
            }

def get_total_dimensions(primary_dimension, secondary_dimensions):
    """
    This function takes in a primary dimension and a list of secondary dimensions and returns a list of all dimensions
    """
    new_list = []
    new_list.append(primary_dimension)
    for dimension in secondary_dimensions:
        new_list.append(dimension)
    return new_list

def get_total_measures(primary_measure, secondary_measures):
    """
    This function takes in a primary measure and a list of secondary measures and returns a list of all measures
    """
    new_list = []
    new_list.append(primary_measure)
    for measure in secondary_measures:
        new_list.append(measure)
    return new_list

def get_dimension_fstring(dimensions):
    """
    This function takes in a list of dimensions and returns a string of all dimensions.
    This is then used to create the state variable which will be used by the program after redirection from Cognito
    """
    dimension_fstring = ''
    for dimension in dimensions:
        dimension_fstring = dimension_fstring + (f"p.pDimensions={dimension}&")
    return dimension_fstring[:-1]

def get_measure_fstring(measures):
    """
    This function takes in a list of measures and returns a string of all measures.
    This is then used to create the state variable which will be used by the program after redirection from Cognito
    """
    measure_fstring = ''
    for measure in measures:
        measure_fstring = measure_fstring + (f"p.pMeasures={measure}&")
    return measure_fstring[:-1]

def get_dashboard_definition(client, account_id, dashboard_id):
    """
    This function takes in a dashboard id and returns the dashboard definition.
    """
    target_dashboard_definition = client.describe_dashboard_definition(
        AwsAccountId=account_id,
        DashboardId=dashboard_id
    )
    return target_dashboard_definition

def set_dataset_identifier_declarations(client, account_id, dashboard_definition, dataset_id):
    """
    This function takes in a dashboard definition and a dataset id and returns the dashboard definition with the dataset identifier declarations added.
    """
    describe_dataset_response = client.describe_data_set(
        AwsAccountId=account_id,
        DataSetId=dataset_id
        )
    dataset_identifier = describe_dataset_response["DataSet"]["Name"]
    dataset_arn = describe_dataset_response["DataSet"]["Arn"]

    dashboard_definition["Definition"]["DataSetIdentifierDeclarations"].append(
        {
            "Identifier": dataset_identifier,
            "DataSetArn": dataset_arn
        }
    )
    return dashboard_definition

def create_table_visual():
    """
    This function creates a table visual skeleton for the target dashboard.
    """
    table_visual = {
        "TableVisual": {
            "VisualId": "d74675d9-8a31-4a27-9609-2e3c274b7071",
            "Title": {
                "Visibility": "VISIBLE"
            },
            "Subtitle": {
                "Visibility": "VISIBLE"
            },
            "ChartConfiguration": {
                "FieldWells": {
                    "TableAggregatedFieldWells": {
                        "GroupBy": [
                        ],
                        "Values": [
                        ]
                    }
                },
                "SortConfiguration": {}
            },
            "Actions": []
        }
    }
    return table_visual

def dimension_updater(dimension):
    """
    This function creates a dimension skeleton for the target dashboard.
    """
    configuration = {
        "CategoricalDimensionField": {
            "FieldId": f"{uuid.uuid4()}.{dimension}",
            "Column": {
                "DataSetIdentifier": "saas_sales_qs_test-rename",
                "ColumnName": dimension
            }
        }
    }
    return configuration

def measure_updater(measure):
    """
    This function creates a measure skeleton for the target dashboard.
    """
    configuration = {
        "NumericalMeasureField": {
            "FieldId": f"{uuid.uuid4()}.{measure}",
            "Column": {
                "DataSetIdentifier": "saas_sales_qs_test-rename",
                "ColumnName": measure
            },
            "AggregationFunction": {
                "SimpleNumericalAggregation": "SUM"
            }
        }
    }
    return configuration

def update_table_visual(dimensions, measures, dashboard_definition, visual):
    """
    This function takes in a list of dimensions and a list of measures and updates the table visual in the dashboard definition.
    """
    dimensions_list = visual["TableVisual"]["ChartConfiguration"]["FieldWells"]["TableAggregatedFieldWells"]["GroupBy"]
    measures_list = visual["TableVisual"]["ChartConfiguration"]["FieldWells"]["TableAggregatedFieldWells"]["Values"]
    target_visuals = dashboard_definition["Definition"]["Sheets"][0]["Visuals"]

    if type(dimensions) == list:
        for dimension in dimensions:
            dimension = dimension_updater(dimension)
            dimensions_list.append(dimension)
    else:
        dimensions_list.append(dimension_updater(dimensions))
        
    
    if type(measures) == list:
        for measure in measures:
            measure = measure_updater(measure)
            measures_list.append(measure)
    else:
        measures_list.append(measure_updater(measures))

    target_visuals.append(visual)
    return dashboard_definition

def delete_existing_dashboard(account_id, dashboard_id, client):
    """
    This function takes in a dashboard id and deletes the dashboard if it exists.
    """
    try:
        client.delete_dashboard(
            AwsAccountId=account_id,
            DashboardId=dashboard_id
        )
    except:
        pass

def publish_dashboard_to_quicksight(account_id, dashboard_id, dashboard_name, dashboard_definition, user_name, client):
    """
    This function takes in a dashboard id, dashboard name, dashboard definition, user name and publishes the dashboard to QuickSight.
    """
    try:
        client.create_dashboard(
            AwsAccountId=account_id,
            DashboardId=dashboard_id,
            Name=dashboard_name,
            Definition=dashboard_definition["Definition"],
            Permissions=[
                {
                    'Principal': f'arn:aws:quicksight:us-east-1:{account_id}:user/default/{user_name}',
                    'Actions': [
                        'quicksight:DescribeDashboard',
                        'quicksight:ListDashboardVersions',
                        'quicksight:UpdateDashboardPermissions',
                        'quicksight:QueryDashboard',
                        'quicksight:UpdateDashboard',
                        'quicksight:DeleteDashboard',
                        'quicksight:DescribeDashboardPermissions',
                        'quicksight:UpdateDashboardPublishedVersion'
                    ]
                }
            ]
        )
        return f"Dashboard {dashboard_id} published successfully"

    except Exception as e:
        return e
