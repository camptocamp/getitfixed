<%!
import os
%>
COMPOSE_PROJECT_NAME=getitfixed

DOCKER_PORT=${os.environ['DOCKER_PORT']}
DOCKER_BASE=${os.environ['DOCKER_BASE']}
DOCKER_TAG=${os.environ['DOCKER_TAG']}

PGHOST=${os.environ['PGHOST']}
PGHOST_SLAVE=${os.environ['PGHOST_SLAVE']}
PGPORT=${os.environ['PGPORT']}
PGUSER=${os.environ['PGUSER']}
PGPASSWORD=${os.environ['PGPASSWORD']}
PGDATABASE=${os.environ['PGDATABASE']}

VISIBLE_WEB_HOST=${os.environ['VISIBLE_WEB_HOST']}
VISIBLE_WEB_PROTOCOL=${os.environ['VISIBLE_WEB_PROTOCOL']}
VISIBLE_ENTRY_POINT=${os.environ['VISIBLE_ENTRY_POINT']}

PRINT_URL=http://print:8080/print

C2CWSGIUTILS_CONFIG=${'/app/development.ini' if os.environ['DEVELOPMENT'] == 'TRUE' else '/app/production.ini'}

SMTP_USER=${os.environ['SMTP_USER']}
SMTP_PASSWORD=${os.environ['SMTP_PASSWORD']}
