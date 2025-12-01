# Start from AWS Lambda Python 3.11 base image
FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies (for psycopg2, pandas, etc.)
RUN yum install -y gcc gcc-c++ make \
    postgresql-devel \
    python3-devel \
    && yum clean all

# Copy requirements and install
# NumPy 1.24.x has pre-built wheels that work with GCC 7.3.1
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your ETL code and other needed files
COPY etl/ ./etl/
COPY lambda_function.py .

# Lambda entry point (calls your handler in lambda_function.py)
CMD ["lambda_function.lambda_handler"]
