from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DIMAIL",
    settings_files=["settings.toml", ".secrets.toml"],
    ignore_unknown_envvars=True,
)

# `envvar_prefix` = export envvars with `export DIMAIL_FOO=bar`.
# `settings_files` = Load these files in the order.
