import sys
import datetime

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    log_entry = f"\n{timestamp} {message}"
    sys.stderr.write(log_entry + "\n")


