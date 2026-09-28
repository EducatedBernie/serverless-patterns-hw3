Prerequisites

Complete module 2 and module3 or Deploy the SAM application in the start_state directory

Ensure your terminal can authenticate and use the SAM CLI and the AWS CLI.

Deploy the completed module

Find the Cognito User Pool Id from Module 2.
Find the dynamo DB table name from Module 3 


Open a terminal window to the module5/sam-python directory

Run 
sam build. When completed...

Run 

sam deploy  --stack-name <stackname> --resolve-s3 --capabilities CAPABILITY_IAM --parameter-overrides OrdersTablename=<module3 output> Stage=dev UserPool=<module2 output>


## Resources

Workshop content repository - https://gitlab.aws.dev/serverless-tfc-workshops/serverless-workshop-content 






