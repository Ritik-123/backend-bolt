import os, sys, django, subprocess, time, re
from django.db import connection
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_bolt.settings')
django.setup()

from django_celery_beat.models import PeriodicTask, IntervalSchedule
from users.models import User
from django.conf import settings


def validate_ip(ip):
    """Validate if the given IP address is in correct IPv4 format."""
    if ip == "0":
        return "0.0.0.0"
    
    ip_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"  # Matches "x.x.x.x" format
    if not re.match(ip_pattern, ip):
        print(f"Error: Invalid IP address '{ip}'. Please provide a valid IPv4 address.")
        sys.exit(1)

    # Ensure each octet is between 0-255
    parts = ip.split(".")
    if not all(0 <= int(part) <= 255 for part in parts):
        print(f"Error: IP address '{ip}' contains an invalid octet (must be 0-255).")
        sys.exit(1)

    return ip

def validate_port(port):
    """Ensure the port is a valid integer between 1 and 65535."""
    try:
        port = int(port)
        if port < 1 or port > 65535:
            raise ValueError
    except ValueError:
        print("Error: Invalid port number. Please provide a port between 1 and 65535.")
        sys.exit(1)

    return port

def check_django_server(django_process):
    """Checks if Django started successfully by analyzing logs and process status."""
    try:
        stdout, stderr = django_process.communicate(timeout=3)  # Capture output within 3s
    except subprocess.TimeoutExpired:
        # If timeout occurs, assume Django is still running fine
        return True  

    # If process exited (poll() is not None), Django failed to start
    if django_process.poll() is not None:
        print("Error: Django server process exited unexpectedly.")
        print(stderr)  # Show full error details
        return False

    # If there's anything in stderr, treat it as an error
    if stderr.strip():
        print("Error: Django server encountered an issue during startup.")
        print(stderr)  # Show full error message
        return False

    return True  # Django is running fine

def static_files_exist():
    """Check if required static files exist in STATIC_ROOT."""
    static_root = settings.STATIC_ROOT  # Ensure STATIC_ROOT is correctly set
    required_files = ["admin/css/base.css", "admin/js/core.js"]  # Adjust as needed

    if not os.path.exists(static_root):
        return False

    for file in required_files:
        file_path = os.path.join(static_root, file)
        if not os.path.exists(file_path):
            return False  # If any required file is missing, return False

    return True  # All required files exist


def run_command(command):
    """Runs a command in a separate process and returns the process object."""
    return subprocess.Popen(command, shell=True)

def table_exists(table_name):
    """Check if a table exists in the database."""
    return table_name in connection.introspection.table_names()

def reset_celery_tasks():
    """Deletes all Celery periodic tasks and schedules to start fresh."""
    PeriodicTask.objects.all().delete()
    # IntervalSchedule.objects.all().delete()


def deploy(server_port):
    """
    **Used to run all necessary commands before starting Django & Celery.**
        
        1. Make-Migrations  
        2. Migrate  
        3. Create Super Admin    
        5. Create Log Directory    
        7. Start Django Server  
        8. Start Celery Worker  
        9. Start Celery Beat  
    """
    call_command('makemigrations')
    
    call_command('migrate')

    # Create Super Admin if not exists
    # if not User.objects.filter(is_staff=True).exists():
    call_command('createsuperadmin')

    # Create logs and archive directories
    # base_path = os.getcwd()
    # log_path, archive_path = os.path.join(base_path, 'logs'), os.path.join(base_path, 'archive')
    # if not os.path.exists(log_path) or not os.path.exists(archive_path):
    call_command('createlogdir')

    # Check if cache table exists, if not create it
    # cache_table_name = "CacheTable"
    # if not table_exists(cache_table_name):
    #     call_command('createcachetable')

    # if not static_files_exist():
    #     call_command('collectstatic', '--noinput')

    # Ensure valid port format
    if ":" in server_port:
        ip, port = server_port.split(":")
        ip = validate_ip(ip)
        port = validate_port(port)
    else:
        ip = "0.0.0.0"  # Default to all interfaces
        port = validate_port(server_port)

    # server_address = f"{ip}:{port}"

    # Start Django server
    # django_server = run_command(f"python manage.py runserver {server_address}")
    # django_server= run_command(f"daphne -b {ip} -p {port} backend_bolt.asgi:application")
    django_server= run_command(f"uvicorn --ws auto --workers 4 --reload --host {ip} --port {port} backend_bolt.asgi:application")

    time.sleep(3)  # Allow Django to start before launching Celery

    # validate django server dynamically:
    if not check_django_server(django_server):
        sys.exit(1)

    print("Starting Celery Worker...")
    celery_worker = run_command("celery -A backend_bolt worker --loglevel=info")

    time.sleep(3)  # Ensure worker starts properly

    print("Starting Celery Beat...")
    celery_beat = run_command("celery -A backend_bolt beat --loglevel=info")

    try:
        django_server.wait()
        celery_worker.wait()
        celery_beat.wait()
    except KeyboardInterrupt:
        print("\n Stopping all services...")
        django_server.terminate()
        celery_worker.terminate()
        celery_beat.terminate()
        reset_celery_tasks()


if __name__ == '__main__':
    # Default port is 8000 if not provided
    server_port = sys.argv[1] if len(sys.argv) > 1 else "8000"
    deploy(server_port)