source .env
echo XML: $INVALID_XML_BUCKET

awslocal s3api create-bucket --bucket $INVALID_XML_BUCKET
