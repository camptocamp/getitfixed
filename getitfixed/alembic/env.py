import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool, text

from alembic import context

from getitfixed.scripts import wait_for_db

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(context.config.config_file_name)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_config():
    conf = context.config.get_section(context.config.config_ini_section)

    # Load config from c2cgeoportal if available
    app_cfg = context.config.get_main_option("app.cfg")
    if app_cfg:
        from c2c.template.config import config

        config.init(context.config.get_main_option("app.cfg"))
        conf.update(config.get_config())

    if "sqlalchemy.url" not in conf:
        conf[
            "sqlalchemy.url"
        ] = "postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}".format(
            **os.environ
        )
    conf.update(
        {"version_table_schema": conf.get("getitfixed", {}).get("schema", "getitfixed")}
    )

    # for 'autogenerate' support
    from getitfixed import models  # noqa

    conf["target_metadata"] = models.meta.Base.metadata

    return conf


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
    context.configure(url=conf["sqlalchemy.url"], literal_binds=True, **conf)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    conf = get_config()
    schema = conf.get("getitfixed", {}).get("schema", "getitfixed")

    connectable = engine_from_config(
        conf, prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    def include_object(
        obj, name, type_, reflected, compare_to
    ):  # pylint: disable=unused-argument
        if type_ == "table":
            return obj.schema == schema
        else:
            return obj.table.schema == schema

    wait_for_db(connectable)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            include_schemas=True,
            include_object=include_object,
            **conf
        )

        connection.execute(text('CREATE SCHEMA IF NOT EXISTS "{}";'.format(schema)))

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
