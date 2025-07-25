import logging.config, sys
import os, time, shutil, zipfile, logging, re
from django.conf import settings
from celery import shared_task
from django.core.mail import send_mail



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')       # Logs Directory
ARCHIVE_DIR = os.path.join(BASE_DIR, 'archive')  # Archive Directory

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

LOGGERS = ["access", "server"]


logger= logging.getLogger('server')
logger.propagate = False

@shared_task
def trigger_log_entry():
    """
    Write an entry to each logger to force log file creation.
    """
    for logger_name in LOGGERS:
        logger = logging.getLogger(logger_name)
        logger.info("Log rotation complete. New log file initialized.")

@shared_task
def move_rotated_logs(log_prefixes=("access", "server")):
        """
        Moves rotated log files matching the pattern `logname.log.YYYY-MM-DD_HH-MM`
        from log_dir to archive_folder.
        
        :param log_dir: Directory containing the log files.
        :param log_prefixes: Tuple of log file prefixes to match.
        """
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(BASE_DIR, 'logs')       # Logs Directory
        arc_dir = os.path.join(BASE_DIR, 'archive')  # Archive Directory

        # Regex pattern
        log_pattern = re.compile(rf"^({'|'.join(log_prefixes)})\.log\.\d{{4}}-\d{{2}}-\d{{2}}$")   #  _\d{{2}}-\d{{2}}$")

        matched_files = [file for file in os.listdir(log_dir) if log_pattern.fullmatch(file)]

        if not matched_files:
            return

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        archive_folder = os.path.join(arc_dir, f"Logs_{timestamp}")

        # Ensure the archive folder exists before moving files
        os.makedirs(archive_folder, exist_ok=True)

        # Move matching rotated log files
        for file in matched_files:
            src, dest = os.path.join(log_dir, file), os.path.join(archive_folder, file)
            shutil.move(src, dest)


# Function to send email notifications
@shared_task
def order_status_email(**kwargs):
    """
    Function to send order status update email.
    """
    id= kwargs.get('id')
    username= kwargs.get('username')
    order_status= kwargs.get('order_status')
    email= kwargs.get('email')
    subject = f"Your order {id} status has changed"
    message = f"Hi {username},\n\nYour order status is now: {order_status}"
    send_mail(subject, message, 'noreply@teambolt.com', [email], fail_silently=False)
    if send_mail:
        logger.info(f"Order status email sent to {email} for order {id}")
    else:
         logger.error(f"Failed to send order status email to {email} for order {id}")
