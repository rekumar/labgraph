from typing import Optional
import toml
import os
from getpass import getpass
from pydantic import BaseModel

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(CURRENT_DIR, "labgraph_config.toml")


class MongoDBConfigValidator(BaseModel):
    host: str
    port: int
    db_name: str
    username: Optional[str]
    password: Optional[str]


class ConfigValidator(BaseModel):
    mongodb: dict


def validate_config(config: dict):
    """Validates the config file. Raises an exception if the config file is invalid.

    Args:
        config (dict): The config file to validate.

    Raises:
        ValueError: The config file is invalid.
    """
    try:
        ConfigValidator(**config)
    except Exception as e:
        raise ValueError(
            f"The config file is invalid. Please check the config file and try again. You can use `labgraph.utils.make_config()` to walk you through creating a valid config file. Error: {e}"
        )


def get_config():
    config_path = os.getenv("LABGRAPH_CONFIG", DEFAULT_CONFIG_PATH)
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = toml.load(f)
    except FileNotFoundError:
        raise ValueError(
            "Labgraph config file was not found. Please set your computer's environment variable 'LABGRAPH_CONFIG' to the path to the config file. If you need help with this, you can run `labgraph.utils.make_config()` to create a config file for you."
        )

    validate_config(config)

    return config


def make_config():
    """Command line tool to help create a config file for Labgraph. The config file is a TOML file that contains the information needed to connect to a MongoDB instance hosting the Labgraph databa5.

    Raises:
        ValueError: Invalid file extension. Must be a .toml file.
        Exception: Unable to write config file to the specified path.
    """
    config_path = os.getenv("LABGRAPH_CONFIG", DEFAULT_CONFIG_PATH)

    filepath = None
    warn_for_envvar = False
    if os.path.exists(config_path):
        print(f"A labgraph config file already exists at {config_path}.\n")
        response = input(
            "Do you want to:\n\t[u]pdate this config file\n\t[r]eplace this config file\n\t[e]xit\n\n[u/r/e]: "
        )
        if response == "u":
            filepath = os.path.abspath(config_path)
        elif response == "r":
            os.remove(config_path)
            if filepath != DEFAULT_CONFIG_PATH:
                warn_for_envvar = True
            pass
        else:
            print("Nothing was changed.")
            return

    if filepath is None:
        warn_for_envvar = True
        filepath = input(
            f"Enter the path to the new config file. (Leave blank for default location: {DEFAULT_CONFIG_PATH}): "
        )
        if filepath == "":
            warn_for_envvar = False
            filepath = DEFAULT_CONFIG_PATH
        filepath = os.path.abspath(filepath)
        if not os.path.basename(filepath).endswith(".toml"):
            raise ValueError(
                f"Config file must be a TOML file! The file should end with extension '.toml'. You provided {filepath}"
            )

    print(f"We will create a config file for you at {filepath}.")
    if warn_for_envvar:
        print(
            f"\nWARNING: Do not forget to create/update an environment variable LABGRAPH_CONFIG to point to {filepath}!\n\nYou have chosen not to put your labgraph config in the default location, so Labgraph requires the environment variable to know where to find your config file. If this is confusing, please restart this function and leave the filepath blank to use the default location.\n"
        )
        response = input("Do you want to continue? [y/n]: ")
        if response != "y":
            print("Nothing was changed.")
            return

    print(
        "Please enter the following information to point Labgraph to the correct MongoDB instance!\n"
    )

    config_dict = {"mongodb": {}}

    config_dict["mongodb"]["host"] = (
        input("Enter MongoDB host (leave blank for default = localhost): ")
        or "localhost"
    )
    port = input("Enter MongoDB port (leave blank for default = 27017): ") or 27017
    config_dict["mongodb"]["port"] = int(port)

    config_dict["mongodb"]["db_name"] = (
        input("Enter database name (leave blank for default = Labgraph): ")
        or "Labgraph"
    )

    db_user = input("Enter username (leave blank if not required): ")
    if db_user != "":
        config_dict["mongodb"]["username"] = db_user
        config_dict["mongodb"]["password"] = getpass(
            "Enter password (typed characters hidden for privacy): "
        )

    validate_config(config_dict)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            toml.dump(config_dict, f)
    except Exception as e:
        raise Exception(
            "Labgraph was unable to write your config file. Error message: ", e
        )

    print(
        f"\nConfig file successfully written to {filepath}. \nWARNING: If you aren't using the default location, please remember to set the environment variable LABGRAPH_CONFIG = {filepath}. \nWARNING: You should restart your Python kernel to ensure that Labgraph uses the new config file."
    )
