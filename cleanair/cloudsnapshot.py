import boto3
from botocore.exceptions import ClientError
import click

session = boto3.Session(profile_name='cloudsnapshot')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []
    if project:
        filters = [{'Name':'tag:Project','Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

def has_pending_snapshots(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

@click.group()
def cli():
    """Clean_Air manages snapshots"""

@cli.group('volumes')
def volumes():
    """Command for volumes"""

@cli.group('snapshots')
def snapshots():
    """Command for snapshots"""

@cli.group('instances')
def instances():
    """Command for instances"""

@volumes.command('list')
@click.option('--project', default=None, help="Only volumes for project(tag Project: <name>)")
def list_volumes(project):
    "List EC2 volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(",".join((
                v.id,
                i.id,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted",
            )))
    return

@snapshots.command('list')
@click.option('--all', 'list_all', default=False, is_flag=True, help="List all snapshots, not most recent)")
@click.option('--project', default=None, help="Only snapshots for project(tag Project: <name>)")
def list_snapshots(project, list_all):
    "List EC2 snapshots"

    instances = filter_instances(project)

    snappy = None

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(",".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))
                
                if s.state == 'completed' and not 'list_all': break
    return

@instances.command('list')
@click.option('--project', default=None, help="Only instances for project(tag Project: <name>)")
def list_instances(project):
    "List EC2 instances"
    
    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']:t['Value'] for t in i.tags or []}
        print(i)
        print(','.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project','<no project>')
        )))

@instances.command('snapshot', help='Create snapshots of all volumes')
@click.option('--project', default=None, help='Only instances for the project')
def create_snapshots(project):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if has_pending_snapshots(v):
                print("Skipping {0}, snapshots already in progress".format(v.id))
                continue
            print("Creating snapshots of {0}".format(v.id))
            v.create_snapshot(Description="Created by Clean Air")
        i.start()
        i.wait_until_running()

    print("Job's done!")

    return

@instances.command('start')
@click.option('--project', default=None, help='Only instances for the project')
def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except ClientError as e:
            print("Could not start {0}".format(i.id))
            continue
    return


@instances.command('stop')
@click.option('--project', default=None, help='Only instances for the project')
def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except ClientError as e:
            print("Could not stop {0}".format(i.id))
            continue
    return


if __name__ == '__main__':
    cli()