FROM python:3.10

WORKDIR /backend_bolt

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script and make it executable
COPY deploy.sh /deploy.sh
RUN chmod +x /deploy.sh
# Set the entrypoint script to run when the container starts
ENTRYPOINT ["/deploy.sh"]