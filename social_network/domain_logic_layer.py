"""
Module for managing domain logic (e.g., user-exist checks and cascading deletions)
and calling CRUD functionality.
"""

from functools import partial
import uuid
from loguru import logger
from social_network.data_access_layer import (
    add_object,
    update_object,
    delete_object,
    get_object,
    get_objects,
    delete_objects,
)
from social_network.validators import tag_normalizer, safe_parse_tags
from social_network.logging_decorator import log_decorator as log

# --- Constants ---
USER_ID_FIELD = "user_id"
STATUS_ID_FIELD = "status_id"
PICTURE_ID_FIELD = "picture_id"
FILE_NAME_FIELD = "file_name"

# --- User CRUD ---
add_user = partial(add_object, field_name=USER_ID_FIELD)
update_user = partial(update_object, field_name=USER_ID_FIELD)
delete_user_core = partial(delete_object, field_name=USER_ID_FIELD)
search_user = partial(get_object, field_name=USER_ID_FIELD)

# --- Status CRUD ---
add_status_core = partial(add_object, field_name=STATUS_ID_FIELD)
update_status = partial(update_object, field_name=STATUS_ID_FIELD)
delete_status = partial(delete_object, field_name=STATUS_ID_FIELD)
search_status = partial(get_object, field_name=STATUS_ID_FIELD)
search_statuses_by_user = partial(get_objects, field_name=USER_ID_FIELD)
delete_statuses_by_user = partial(delete_objects, field_name=USER_ID_FIELD)


# --- Picture CRUD ---
@log
def add_picture_core(picture_data, picture_id, *, table):
    """
    Add a picture record. Returns True if successful, False otherwise.
    """
    return add_object(picture_data, picture_id, field_name="picture_id", table=table)


update_picture = partial(update_object, field_name=PICTURE_ID_FIELD)
delete_picture = partial(delete_object, field_name=PICTURE_ID_FIELD)
search_picture = partial(get_object, field_name=PICTURE_ID_FIELD)
search_pictures_by_user = partial(get_objects, field_name=USER_ID_FIELD)
delete_pictures_by_user = partial(delete_objects, field_name=USER_ID_FIELD)


# --- Composite Logic ---
@log
def delete_user(user_id, user_table, status_table, picture_table):
    """
    Deletes a user and any associated statuses and pictures (cascading behavior).

    :param user_id: User ID to delete
    :param user_table: Table object for user records
    :param status_table: Table object for status records
    :param picture_table: Table object for picture records
    :return: True if deletion successful, else False
    """
    delete_statuses_by_user(record_id=user_id, table=status_table)
    delete_pictures_by_user(record_id=user_id, table=picture_table)
    return delete_user_core(record_id=user_id, table=user_table)


@log
def add_status(status_data, user_table, status_table):
    """
    Adds a status record after verifying that the associated user exists.

    Enforces a referential integrity check by confirming that the user_id
    in the status_data exists in the user table before proceeding with insert.

    :param status_data: Dictionary containing 'status_id', 'user_id', and 'status_text'
    :param user_table: DataSet table object for users
    :param status_table: DataSet table object for statuses
    :return: True if status was added successfully, False otherwise
    """
    if not search_user(status_data["user_id"], table=user_table):
        logger.warning(
            "ADD FAILURE: User {} not found in user table", status_data["user_id"]
        )
        return False
    return add_status_core(status_data, status_data["status_id"], table=status_table)


@log
def add_picture(picture_data, user_table, picture_table):
    """
    Adds a picture record after validating that the associated user exists.
    Performs tag normalization and generates a UUID if not provided.
    After insertion, retrieves the record to access its auto-generated ID
    and updates the record with a derived file_name based on that ID.

    :param picture_data: Dict containing picture fields
    :param user_table: User table object (for user existence validation)
    :param picture_table: Picture table object
    :return: The inserted picture (with tags parsed), or False if creation failed
    """
    user_id = picture_data.get("user_id")
    if not get_object(user_id, field_name="user_id", table=user_table):
        logger.warning("User {} does not exist. Cannot add picture.", user_id)
        return False

    picture_data["tags"] = tag_normalizer(picture_data.get("tags", ""))

    if "picture_id" not in picture_data or not picture_data["picture_id"]:
        picture_data["picture_id"] = uuid.uuid4().hex

    picture_id = picture_data["picture_id"]

    # Step 1: Insert without file_name
    picture_data.pop("file_name", None)  # Ensure we don't pre-fill it
    success = add_picture_core(picture_data, picture_id, table=picture_table)
    if not success:
        logger.warning("Failed to add picture record.")
        return False

    # Step 2: Retrieve record after it's fully persisted
    picture = get_object(picture_id, field_name="picture_id", table=picture_table)
    if not picture:
        logger.warning(
            "Record added but retrieval failed for picture_id {}", picture_id
        )
        return False

    # Step 3: Update with derived file_name
    file_name = generate_normalized_filename(picture["id"])
    update_success = update_picture(
        {"file_name": file_name}, picture_id, table=picture_table
    )

    if not update_success:
        logger.warning(
            "Failed to set file_name after insert for picture_id {}", picture_id
        )
        return False

    # Step 4: Parse tags before returning
    picture = get_object(picture_id, field_name="picture_id", table=picture_table)
    return safe_parse_tags(picture)


@log
def generate_normalized_filename(record_id, extension="png"):
    """
    Returns a zero-padded filename string with a given extension (default: png).
    E.g., 42 -> "0000000042.png"
    """
    return str(record_id).zfill(10) + f".{extension}"
