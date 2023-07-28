FROM public.ecr.aws/lambda/python:3.10

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

ENV PYTHONPATH "${PYTHONPATH}:" ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

RUN yum -y install redhat-rpm-config python-devel python-pip python-cffi libffi-devel cairo pango gdk-pixbuf2

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "index.handler" ]