# app/services/cartography_companion/mock/seeders.py

import logging
import boto3
from typing import Any

logger = logging.getLogger(__name__)


def seed_vpcs(client: Any, data: list[dict]) -> dict[str, str]:
    """
    Creates VPCs in Moto. Returns {cidr -> vpc_id} mapping
    so downstream seeders (subnets, SGs) can reference them.
    """
    vpc_map: dict[str, str] = {}
    for vpc in data:
        response = client.create_vpc(CidrBlock=vpc["CidrBlock"])
        vpc_id = response["Vpc"]["VpcId"]
        vpc_map[vpc["CidrBlock"]] = vpc_id

        if vpc.get("Tags"):
            client.create_tags(Resources=[vpc_id], Tags=vpc["Tags"])

        # Enable DNS if specified
        if vpc.get("EnableDnsHostnames"):
            client.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsHostnames={"Value": True},
            )

    logger.debug(f"Seeded {len(vpc_map)} VPCs")
    return vpc_map


def seed_subnets(client: Any, data: list[dict], vpc_map: dict[str, str]) -> dict[str, str]:
    """
    Creates subnets. vpc_map from seed_vpcs maps cidr->vpc_id.
    Falls back to first available VPC if fixture references unknown VPC.
    """
    subnet_map: dict[str, str] = {}
    fallback_vpc = next(iter(vpc_map.values())) if vpc_map else None

    for subnet in data:
        vpc_id = vpc_map.get(subnet.get("VpcCidr", ""), fallback_vpc)
        if not vpc_id:
            logger.warning(f"No VPC found for subnet {subnet.get('CidrBlock')} — skipping")
            continue

        response = client.create_subnet(
            VpcId=vpc_id,
            CidrBlock=subnet["CidrBlock"],
            AvailabilityZone=subnet.get("AvailabilityZone", "us-east-1a"),
        )
        subnet_id = response["Subnet"]["SubnetId"]
        subnet_map[subnet["CidrBlock"]] = subnet_id

        if subnet.get("Tags"):
            client.create_tags(Resources=[subnet_id], Tags=subnet["Tags"])

    logger.debug(f"Seeded {len(subnet_map)} subnets")
    return subnet_map


def seed_security_groups(
    client: Any,
    data: list[dict],
    vpc_map: dict[str, str],
) -> dict[str, str]:
    """Returns {fixture_name -> sg_id} mapping."""
    sg_map: dict[str, str] = {}
    fallback_vpc = next(iter(vpc_map.values())) if vpc_map else None

    for sg in data:
        vpc_id = vpc_map.get(sg.get("VpcCidr", ""), fallback_vpc)
        response = client.create_security_group(
            GroupName=sg["GroupName"],
            Description=sg.get("Description", "mock sg"),
            VpcId=vpc_id,
        )
        sg_id = response["GroupId"]
        sg_map[sg["GroupName"]] = sg_id

        # Add ingress rules
        if sg.get("IpPermissions"):
            client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=sg["IpPermissions"],
            )

        # Add egress rules
        if sg.get("IpPermissionsEgress"):
            client.authorize_security_group_egress(
                GroupId=sg_id,
                IpPermissions=sg["IpPermissionsEgress"],
            )

        if sg.get("Tags"):
            client.create_tags(Resources=[sg_id], Tags=sg["Tags"])

    logger.debug(f"Seeded {len(sg_map)} security groups")
    return sg_map


def seed_ec2_instances(
    client: Any,
    data: list[dict],
    sg_map: dict[str, str],
    subnet_map: dict[str, str],
) -> None:
    for instance in data:
        # Resolve SG names to IDs seeded in Moto
        sg_ids = [sg_map.get(name, name) for name in instance.get("SecurityGroupNames", [])]
        subnet_id = subnet_map.get(instance.get("SubnetCidr", ""))

        kwargs: dict = {
            "ImageId": instance.get("ImageId", "ami-12345678"),
            "MinCount": 1,
            "MaxCount": 1,
            "InstanceType": instance.get("InstanceType", "t3.micro"),
        }
        if sg_ids:
            kwargs["SecurityGroupIds"] = sg_ids
        if subnet_id:
            kwargs["SubnetId"] = subnet_id

        response = client.run_instances(**kwargs)
        instance_id = response["Instances"][0]["InstanceId"]

        if instance.get("Tags"):
            client.create_tags(Resources=[instance_id], Tags=instance["Tags"])

    logger.debug(f"Seeded {len(data)} EC2 instances")


def seed_lambdas(
    lambda_client: Any, data: list[dict], role_arn: str = "arn:aws:iam::123456789012:role/mock-role"
) -> None:
    import zipfile, io

    # Moto needs a valid zip for lambda code
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("handler.py", "def handler(event, context): pass")
    zip_bytes = zip_buffer.getvalue()

    for fn in data:
        lambda_client.create_function(
            FunctionName=fn["FunctionName"],
            Runtime=fn.get("Runtime", "python3.11"),
            Role=fn.get("Role", role_arn),
            Handler=fn.get("Handler", "handler.handler"),
            Code={"ZipFile": zip_bytes},
            Environment={"Variables": fn.get("Environment", {})},
            VpcConfig=fn.get("VpcConfig", {}),
            Timeout=fn.get("Timeout", 30),
            MemorySize=fn.get("MemorySize", 128),
        )
    logger.debug(f"Seeded {len(data)} Lambda functions")


def seed_iam_roles(iam_client: Any, data: list[dict]) -> dict[str, str]:
    """Returns {role_name -> role_arn}."""
    import json

    role_map: dict[str, str] = {}
    default_policy = json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    )

    for role in data:
        response = iam_client.create_role(
            RoleName=role["RoleName"],
            AssumeRolePolicyDocument=role.get("AssumeRolePolicyDocument", default_policy),
            Description=role.get("Description", ""),
            Path=role.get("Path", "/"),
        )
        role_arn = response["Role"]["Arn"]
        role_map[role["RoleName"]] = role_arn

        for policy_arn in role.get("ManagedPolicies", []):
            try:
                iam_client.attach_role_policy(RoleName=role["RoleName"], PolicyArn=policy_arn)
            except Exception:
                pass  # policy may not exist in Moto

    logger.debug(f"Seeded {len(role_map)} IAM roles")
    return role_map


def seed_dynamodb_tables(dynamodb_client: Any, data: list[dict]) -> None:
    for table in data:
        dynamodb_client.create_table(
            TableName=table["TableName"],
            KeySchema=table["KeySchema"],
            AttributeDefinitions=table["AttributeDefinitions"],
            BillingMode=table.get("BillingMode", "PAY_PER_REQUEST"),
        )
    logger.debug(f"Seeded {len(data)} DynamoDB tables")
