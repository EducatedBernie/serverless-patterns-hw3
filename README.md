# Serverless Patterns Workshop Modules 1 to 5

This repository contains the code deployed for the five required modules of the [AWS Serverless Patterns workshop](https://catalog.workshops.aws/serverless-patterns/en-US). The AWS account region was `us-east-2`. Each module has its own AWS SAM template and CloudFormation stack.

| Module | Source folder | Stack | Verified result |
| --- | --- | --- | --- |
| 1 Intro to Serverless | `module1/` | `serverless-patterns-m1` | REST `GET /users` returned HTTP 200 and four records. |
| 2 Synchronous Invocation | `ws-serverless-patterns/users/` | `ws-serverless-patterns-users` | Regular user could access their own record; admin could list users; the API rejected unauthenticated requests. Unit tests passed. |
| 3 Synchronous Idempotence | `ws-serverless-patterns/orders/` | `ws-serverless-patterns-orders` | Repeating the same order request returned success twice and stored one order. |
| 4 Asynchronous Invocation | `ws-serverless-patterns/userprofile/` | `ws-serverless-patterns-userprofile` | Address and favorite requests were accepted, then appeared in their DynamoDB tables after EventBridge and SQS processing. |
| 5 Polling | `ws-serverless-patterns/orderstatus/` | `ws-serverless-patterns-orderstatus` | The order status changed from `PLACED` to `PREPARING` after an EventBridge event and a later API poll returned the new state. |

Modules 2 to 5 start from the workshop's supplied SAM archives. Changes in this repository include Python 3.12 runtime and layer compatibility, scoped DynamoDB permissions, a JWT authorizer for Module 2, and a Module 5 status update that preserves the existing order record. Module 1 was implemented with a SAM template instead of manual console setup. The `evidence/` directory is local only and is excluded from Git; screenshots and test output are in the Word report.

The stack names above are needed for the workshop cleanup. Delete the order status stack before the orders stack, then delete the user profile, users, and Module 1 stacks. Verify each stack is gone in CloudFormation. The AWS SAM CLI managed bucket stack is separate and can be removed after all workshop deployments are no longer needed.
