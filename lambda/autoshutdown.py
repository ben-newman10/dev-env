import boto3


def handler(event, context):
    ec2 = boto3.resource("ec2")

    instances = ec2.instances.filter(
        Filters=[{"Name": "tag:autoshutdown", "Values": ["true"]}]
    )

    RunningInstances = []

    for instance in instances:
        if instance.state["Name"] == "running":
            RunningInstances.append(instance.id)

    if len(RunningInstances) > 0:
        shuttingDown = ec2.instances.filter(InstanceIds=RunningInstances).stop()
        print(shuttingDown)
    else:
        print("Nothing to see here")
