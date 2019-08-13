
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from c2c.template.config import config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(context.config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from getitfixed import models  # noqa
target_metadata = models.meta.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_config():
    config.init(context.config.get_main_option('app.cfg'))
    settings = {}
    settings.update(config.get_config())
    settings.update({
        'script_location': context.config.get_main_option('script_location'),
        'version_table': context.config.get_main_option('version_table'),
        'version_locations': context.config.get_main_option('version_locations'),
        'version_table_schema': settings.get('schema_getitfixed', 'getitfixed')
    })
    return settings


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    conf = get_config()
    context.configure(url=conf['sqlalchemy.url'],
                      target_metadata=target_metadata,
                      literal_binds=True,
                      **conf)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    conf = get_config()

    connectable = engine_from_config(
        conf,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    def include_object(obj, name, type_, reflected, compare_to):  # pylint: disable=unused-argument
        if type_ == 'table':
            return obj.schema == conf.get('version_table_schema')
        else:
            return obj.table.schema == conf.get('version_table_schema')

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            **conf
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
