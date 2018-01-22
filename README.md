# aws-chalice-file-storage

A chalice based simple API for adding and removing image files from AWS S3 Bucket.

## Setup

Note: Make sure you installed and configured [chalice](https://github.com/aws/chalice) and [aws-cli](https://github.com/aws/aws-cli).

### CloudFormation Resources

A CloudFormation template provisions all the resources needed for the application:
* S3 Bucket for storing files
* DynamoDB for indexing stored files

Create the CloudFormation stack using the AWS CLI:

```bash
aws cloudformation create-stack --stack-name aws-chalice-file-storage --template-body file://cloudformation.json 
```

### Chalice Application

File `.chalice/policy-dev.json` contains all requirement policies. The only thing you need to is to deploy your application:

```
$ chalice deploy
```

### Create an API Key

Create an API key for API Gateway endpoint to be used by the user
interface for secure access.

