import boto3

# Function to set CORS configuration for an S3 bucket

def set_cors():
    s3 = boto3.client('s3')
    bucket_name = "multilingual-auto-caption"

    cors_configuration = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'PUT', 'POST', 'HEAD', 'DELETE'],
            'AllowedOrigins': ['*'],  # For development. In prod, restrict to your domain
            'ExposeHeaders': ['ETag']
        }]
    }

    try:
        s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_configuration)
        print(f"Successfully set CORS configuration for bucket: {bucket_name}")
    except Exception as e:
        print(f"Error setting CORS configuration: {e}")

if __name__ == "__main__":
    set_cors()
