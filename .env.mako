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

INI_FILE=${'/app/development.ini' if os.environ['DEVELOPMENT'] == 'TRUE' else '/app/production.ini'}

PROXY_PREFIX=${os.environ['PROXY_PREFIX']}
