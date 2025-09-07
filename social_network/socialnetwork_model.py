"""
Defines schema and access methods for the Users, Status, and Picture tables.

Tables:
- UserTable: Stores user metadata.
- StatusTable: Stores user status updates.
- PictureTable: Stores image metadata and associated tags.

This module uses a hybrid connection strategy:
- A singleton database connection is created using lru_cache.
- A context manager yields this connection for controlled access.

Supports initialization of tables with schema-defining records.
"""

from contextlib import contextmanager
from functools import lru_cache
from loguru import logger
from peewee import IntegrityError, OperationalError
from playhouse.dataset import DataSet
from social_network.logging_decorator import log_decorator as log

DB_FILE = "sqlite:///socialnetwork.db"


@log
@lru_cache(maxsize=1)
def get_dataset_instance():
    """
    Returns a singleton instance of the dataset connection.
    Ensures only one DataSet object is used throughout the application.
    """
    return DataSet(DB_FILE)


@log
@contextmanager
def database_manager():
    """
    Context manager that yields the singleton DataSet instance.
    Ensures compatibility with `with` statements while maintaining singleton behavior.
    """
    db = get_dataset_instance()
    try:
        yield db
    except (OperationalError, IntegrityError) as error:
        logger.error("Database error: {}", error)
        raise


@log
def get_user_table(db):
    """
    Returns a reference to the UserTable from the database.

    :param db: DataSet instance
    :return: Table object for user records
    """
    return db["UserTable"]


@log
def get_status_table(db):
    """
    Returns a reference to the StatusTable from the database.

    :param db: DataSet instance
    :return: Table object for status records
    """
    return db["StatusTable"]


@log
def get_picture_table(db):
    """
    Returns a reference to the PictureTable from the database.

    :param db: DataSet instance
    :return: Table object for picture records
    """
    return db["PictureTable"]


@log
def initialize_database():
    """
    Initializes and returns the User, Status, and Picture tables.

    This function:
    - Creates required tables using Dataset.
    - Inserts temporary schema-defining records to force schema creation.
    - Adds indexes for unique fields.
    - Removes placeholder records to leave a clean schema.

    :return: Tuple (users, status, picture) — references to initialized table objects
    """
    with database_manager() as db:
        users = get_user_table(db)
        logger.info("Users table created")
        try:
            users.insert(
                user_id="<USER_ID>",
                user_name="<NAME>",
                user_last_name="<NAME>",
                user_email="<EMAIL>",
            )
            users.create_index(["user_id"], unique=True)
        except IntegrityError as error:
            logger.warning("Failed to insert schema-defining user entry: {}", error)

        status = get_status_table(db)
        logger.info("Status table created")
        try:
            status.insert(
                status_id="<STATUS_ID>",
                user_id="<USER_ID>",
                status_text="<STATUS TEXT>",
            )
            status.create_index(["status_id"], unique=True)
        except IntegrityError as error:
            logger.warning("Failed to insert schema-defining status entry: {}", error)

        picture = get_picture_table(db)
        logger.info("Picture table created")
        try:
            picture.insert(
                picture_id="<PICTURE_ID>",
                user_id="<USER_ID>",
                tags="<#TAGS>",
                file_name="<FILE_NAME>",
            )
            picture.create_index(["picture_id"], unique=True)
        except IntegrityError as error:
            logger.warning("Failed to insert schema-defining picture entry: {}", error)

        # Clean up the schema-defining records
        for table, field, value in [
            (picture, "picture_id", "<PICTURE_ID>"),
            (status, "status_id", "<STATUS_ID>"),
            (users, "user_id", "<USER_ID>"),
        ]:
            try:
                table.delete(**{field: value})
            except OperationalError as error:
                logger.warning("Failed to delete schema-defining entry: {}", error)

        logger.info("Database initialized.")
        return users, status, picture
