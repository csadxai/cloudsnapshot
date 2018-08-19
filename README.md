# cloudsnapshot

Demo project to manage AWS EC2 snapshot project

## About

This project is a demo, and uses boto3 to manage ec2 instances snapshots.

## Configuring

cloudsnapshot uses the configuration file created by aws cli, e.g. 
`aws configure --profile cloudnsnapshot`

## Running

`pipenv run python cloudsnapshot.py <command> <--project=PROJECT>`

*command* is list, start, or stop
*project* is optional