aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 380665605337.dkr.ecr.us-east-1.amazonaws.com
docker build -t docker-image:pdf-generator .
docker tag docker-image:pdf-generator 380665605337.dkr.ecr.us-east-1.amazonaws.com/pdf-generator:latest
docker push 380665605337.dkr.ecr.us-east-1.amazonaws.com/pdf-generator:latest