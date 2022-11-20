try:
    import tomllib as toml
except ImportError:
    import tomli as toml

with open('config.toml', 'rb') as fp:
    CONFIG = toml.load(fp)
