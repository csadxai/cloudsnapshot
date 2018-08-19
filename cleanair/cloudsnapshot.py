import boto3
import click

session = boto3.Session(profile_name='cloudsnapshot')
ec2 = session.resource('ec2')

@click.command()
@click.option('--project', default=None, help="Only instances for project(tag Project: <name>)")
def list_instances(project):
    "List EC2 instances"
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instance = ec2.instances.filter(Filters=filters)
    else:
        instance = ec2.instances.all()
    for i in instance:
        print(i)
        print(','.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
        )))

if __name__ == '__main__':
    list_instances()