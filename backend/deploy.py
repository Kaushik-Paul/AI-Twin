import os
import shutil
import zipfile
import subprocess
import time

import boto3


def main():
    print("Creating Lambda deployment package...")

    # Clean up
    if os.path.exists("lambda-package"):
        shutil.rmtree("lambda-package")
    if os.path.exists("lambda-deployment.zip"):
        os.remove("lambda-deployment.zip")

    # Create package directory
    os.makedirs("lambda-package")

    # Install dependencies using Docker with Lambda runtime image
    print("Installing dependencies for Lambda runtime...")

    # Use the official AWS Lambda Python 3.12 image
    # This ensures compatibility with Lambda's runtime environment
    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "-v",
            f"{os.getcwd()}:/var/task",
            "--platform",
            "linux/amd64",  # Force x86_64 architecture
            "--entrypoint",
            "",  # Override the default entrypoint
            "public.ecr.aws/lambda/python:3.12",
            "/bin/sh",
            "-c",
            "pip install --target /var/task/lambda-package -r /var/task/requirements.txt --platform manylinux2014_x86_64 --only-binary=:all: --upgrade",
        ],
        check=True,
    )

    # Copy application files
    print("Copying application files...")

    # Ensure backend package directory exists inside the Lambda package
    backend_dest = os.path.join("lambda-package", "backend")
    os.makedirs(backend_dest, exist_ok=True)

    # Copy backend package __init__ so that `backend` is importable
    if os.path.exists("__init__.py"):
        shutil.copy2("__init__.py", backend_dest)

    # Copy the main application package (backend/main)
    main_src = "main"
    main_dest = os.path.join(backend_dest, "main")
    if os.path.exists(main_src):
        shutil.copytree(main_src, main_dest)

    # Copy the Lambda entrypoint
    if os.path.exists("lambda_handler.py"):
        shutil.copy2("lambda_handler.py", "lambda-package/")

    # Copy data directory under backend so ../data paths from backend/main resolve
    if os.path.exists("data"):
        backend_data_dest = os.path.join("lambda-package", "backend", "data")
        shutil.copytree("data", backend_data_dest)

    # Create zip
    print("Creating zip file...")
    with zipfile.ZipFile("lambda-deployment.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("lambda-package"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "lambda-package")
                zipf.write(file_path, arcname)

    # Show package size
    size_mb = os.path.getsize("lambda-deployment.zip") / (1024 * 1024)
    print(f"✓ Created lambda-deployment.zip ({size_mb:.2f} MB)")

    # Deploy via S3 to Lambda
    region = os.getenv("DEFAULT_AWS_REGION", "ap-south-1")
    s3 = boto3.client("s3", region_name=region)
    lambda_client = boto3.client("lambda", region_name=region)

    bucket_name = f"twin-deploy-{int(time.time())}"
    key = "lambda-deployment.zip"

    print(f"Creating temporary S3 bucket {bucket_name} in {region}...")
    create_args = {"Bucket": bucket_name}
    if region != "us-east-1":
        create_args["CreateBucketConfiguration"] = {"LocationConstraint": region}
    s3.create_bucket(**create_args)

    try:
        print("Uploading lambda-deployment.zip to S3...")
        s3.upload_file("lambda-deployment.zip", bucket_name, key)

        print("Updating Lambda function code from S3...")
        lambda_client.update_function_code(
            FunctionName="twin-prod-api",
            S3Bucket=bucket_name,
            S3Key=key,
            Publish=True,
        )
    finally:
        print("Cleaning up S3 object...")
        try:
            s3.delete_object(Bucket=bucket_name, Key=key)
        except Exception:
            pass


if __name__ == "__main__":
    main()