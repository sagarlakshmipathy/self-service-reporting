
# Reader focused Self-Service Reporting in Amazon QuickSight!

## About the project
Today, readers cannot custom reports (tables) in QuickSight or for that matter it is not possible in a lot of tools. You can however use AWS services and QuickSight public APIs to create a system that lets you generate reports as a reader.

This system uses QuickSight Dashboard as a UI to show you the list of columns from a metadata dataset. This frontend dashboard lets users to select the columns they want to see in the target table. 

After the users choose the column names they want to include in the final table, they are expected to hit a `Submit` button. This action is tied to a navigation action which triggers an API call to pass these column names to AWS Lambda. The Lambda function then uses these columns to create a table on demand and creates a new dashboard and deploy it in QuickSight.

After the dashboard creation, the Lambda function redirects readers to the new dashboard i.e. `AdhocReport`, to provide a seamless reader experience in QuickSight. Readers can use the new dashboard to create any number of tables as they wish by selecting the columns and submitting to Lambda.

Here is the high level overview of the architecture:

<img width="1398" alt="image" src="https://user-images.githubusercontent.com/30472234/235336933-cb0bc542-3e75-49b2-b3de-acb7a6fa656e.png">


## Deployment steps

This repoository helps admins setup self service reporting capability for their readers.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Once you have installed the requirements.txt file, you need to verify if you have the pre-requisite packages for CDK

```
$ node -v
$ cdk --version
$ python --version
```

If need be, install

```
$ sudo yum install npm
```
```
$ nvm install 16
```
```
$ npm install -g aws-cdk
```
```
$ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
$ unzip awscliv2.zip
$ sudo ./aws/install
```

At this point you can now synthesize the CloudFormation template for this code. CDK CLI requires you to be in the same folder as cdk.json is present.

```
$ cdk synth
```

```
$ cdk bootstrap
```
```
$ cdk deploy --all
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

### Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

 Enjoy!
