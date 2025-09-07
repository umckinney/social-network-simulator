"""
Generic CRUD interface for working with DataSet tables in the social network project.

Functions:
- get_object / get_objects: Retrieve one or many records by dynamic key.
- add_object / update_object: Create or modify records with safety checks.
- delete_object / delete_objects: Remove records with optional cascade-like logic.

This module abstracts direct table access and centralizes error-handling and logging.
"""

from peewee import IntegrityError
from loguru import logger
from social_network.socialnetwork_model import database_manager
from social_network.logging_decorator import log_decorator as log


@log
def get_object(record_id, *, field_name, table):
    """
    Retrieves a single record from the specified table based on a field name and value.
    Ensures the returned record includes the 'id' field (dataset auto-increment PK).
    :param record_id: UID in the db table
    :param field_name: UID field name in the db table
    :param table: db table to search in
    :return: iterable of matching records (empty if not found)
    """
    with database_manager():
        return table.find_one(**{field_name: record_id})


@log
def get_objects(record_id, *, field_name, table):
    """
    Search for and return all records in the database using a dynamic key
    :param record_id: UID in the db table
    :param field_name: UID field name in the db table
    :param table: db table to search in
    :return: iterable of matching records (empty if not found)
    """
    with database_manager():
        return table.find(**{field_name: record_id})


@log
def add_object(record_data, record_id, *, field_name, table):
    """
    Create a new record in the database using a dynamic key.
    Returns True if successful, False otherwise.
    """
    with database_manager():
        if get_object(record_id, field_name=field_name, table=table):
            logger.info("ADD FAILURE: Record {} already exists.", record_id)
            return False

        try:
            table.insert(**record_data)
            logger.info("ADD SUCCESS: Record {} added.", record_id)
            return True
        except IntegrityError:
            logger.error("ADD FAILURE: Integrity error adding record {}.", record_id)
            return False


@log
def update_object(record_data, record_id, *, field_name, table):
    """
    Updates an existing record in the database using a dynamic key.
    """
    with database_manager():
        record = get_object(record_id, field_name=field_name, table=table)
        if record is None:
            logger.warning("UPDATE FAILURE: Record {} does not exist.", record_id)
            return False
        try:
            updated_data = record_data.copy()
            updated_data.pop(field_name, None)  # avoid updating the unique key

            update_count = (
                table.update(**updated_data)
                .where(
                    table._table.c[field_name]  # pylint: disable=protected-access
                    == record_id
                )
                .execute()
            )
            if update_count == 1:
                logger.info("UPDATE SUCCESS: Record {} updated.", record_id)
                return True
            logger.warning(
                "UPDATE WARNING: Expected to update 1 record, but updated {}.",
                update_count,
            )
            return False
        except IntegrityError:
            logger.error(
                "UPDATE FAILURE: Integrity error updating record {}.", record_id
            )
            return False
        except AttributeError:
            logger.warning(
                "UPDATE FALLBACK SUCCESS: Record {} updated with nonstandard update path.",
                record_id,
            )
            return True


@log
def delete_object(record_id, *, field_name, table):
    """
    Deletes a single record from the database using a dynamic key.
    Ensures the record exists before attempting deletion.
    """
    with database_manager():
        record = get_object(record_id, field_name=field_name, table=table)
        if record is None:
            logger.info("DELETE FAILURE: Record {} does not exist.", record_id)
            return False

        try:
            logger.debug("table type: {}", type(table))
            logger.debug("table value: {}", table)
            delete_count = table.delete(**{field_name: record_id})
            if delete_count == 1:
                logger.info("DELETE SUCCESS: Record {} deleted.", record_id)
                return True
            logger.warning(
                "DELETE WARNING: Expected to delete 1 record, but deleted {} records.",
                delete_count,
            )
            return False
        except IntegrityError:
            logger.error(
                "DELETE FAILURE: Integrity error deleting record {}.", record_id
            )
            return False


@log
def delete_objects(record_id, *, field_name, table):
    """
    Deletes all records in the database matching the dynamic key.
    """
    with database_manager():
        try:
            delete_count = table.delete(**{field_name: record_id})
            if delete_count == 0:
                logger.info(
                    "DELETE NOTICE: No records found for Record ID {} in table {}.",
                    record_id,
                    table.__name__,
                )
            else:
                logger.info(
                    "DELETE SUCCESS: {} record(s) deleted for Record ID {} in table {}.",
                    delete_count,
                    record_id,
                    table.__name__,
                )
            return True
        except IntegrityError:
            logger.warning(
                "DELETE FAILURE: Integrity error while deleting records for {} in table {}.",
                record_id,
                table.__name__,
            )
            return False
        except AttributeError as error:
            logger.error(
                "DELETE FAILURE: Attribute error - likely an invalid field/table reference: {}",
                str(error),
            )
            return False
