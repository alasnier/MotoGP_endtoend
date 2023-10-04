import boto3

# Let's use Amazon S3
s3 = boto3.resource(
    "s3",
    aws_access_key_id="AKIA4SIAAOBGP2VOW5I6",
    aws_secret_access_key="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",
)

print("")
print("")
print("List of bucket(s) available :")
# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)

# Upload into Bucket
bucket = s3.Bucket("motogp-bucket")
bucket.upload_file("collect_motogp_datas.csv", "collect_motogp_datas.csv")

print("")
print("")
print("Verification. List of files into the bucket")
# Verify the upload
for object_summary in bucket.objects.filter():
    print(object_summary.key)
