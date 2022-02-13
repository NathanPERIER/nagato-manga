
import os

# More information on this configuration file here : https://docs.gunicorn.org/en/stable/settings.html#settings


loglevel = 'info'

proc_name = 'nagato-api'

# More than one worker ruins the caching done by the API
# In order to solve this, we should use an external service like Redis
# but this would probably be overkill
threads = 1
workers = 1

nagato_host = os.getenv('NAGATO_HOST') if 'NAGATO_HOST' in os.environ else '0.0.0.0'
nagato_port = os.getenv('NAGATO_PORT') if 'NAGATO_PORT' in os.environ else '8090'
bind = [f"{nagato_host}:{nagato_port}"]
