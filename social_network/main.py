# pylint: disable=protected-access
"""
main driver for a simple social network project
"""

import csv
import re
from functools import lru_cache
from pathlib import Path
from loguru import logger
from social_network.socialnetwork_model import initialize_database
from social_network.domain_logic_layer import (
    add_user as add_user_logic,
    update_user as update_user_logic,
    delete_user as delete_user_logic,
    search_user as search_user_logic,
    add_status as add_status_logic,
    update_status as update_status_logic,
    delete_status as delete_status_logic,
    search_status as search_status_logic,
    search_statuses_by_user as search_statuses_by_user_logic,
    add_picture as add_picture_logic,
    update_picture as update_picture_logic,
    delete_picture as delete_picture_logic,
    search_picture as search_picture_logic,
    search_pictures_by_user as search_pictures_by_user_logic,
)
from social_network.file_structure_manager import create_pointer_file
from social_network.logging_decorator import log_decorator as log
from social_network.validators import safe_parse_tags


@log
@lru_cache(maxsize=1)
def initialize_db():
    """
    Initialize the database and return references to the dataset tables
    """
    return initialize_database()


# pylint: disable=too-many-arguments, too-many-positional-arguments
@log
def load_csv_file(file_name, transform_row, insert_func, table, required_fields, label):
    """
    Generic function for loading a csv file
    """
    try:
        with open(file_name.strip(), "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            logger.debug("Header: {}", csv_reader.fieldnames)

            if not csv_reader.fieldnames or not required_fields.issubset(
                set(csv_reader.fieldnames)
            ):
                logger.warning("Missing required fields: {}", required_fields)
                print(f"File fields are missing required fields: {required_fields}")
                return False

            insertion_counter = 0
            skipped_counter = 0
            for row in csv_reader:
                if any(not value.strip() for value in row.values()):
                    logger.warning("Skipping row with empty fields: {}", row)
                    skipped_counter += 1
                    continue

                data = transform_row(row)

                result = insert_func(data, table)
                if result:
                    insertion_counter += 1
                else:
                    skipped_counter += 1

            total_rows = insertion_counter + skipped_counter
            logger.info("Inserted {} of {} rows", insertion_counter, total_rows)
            logger.info("Skipped {} of {} rows", skipped_counter, total_rows)
            print(f"Inserted {insertion_counter} rows out of {total_rows} total rows")
            print(f"Skipped {skipped_counter} rows out of {total_rows} total rows.")

    except (KeyError, FileNotFoundError) as error:
        logger.error("Error {} occurred when loading {}", error, label)
        return False

    return True


@log
def load_users(file_name, user_table):
    """
    Loads user records from a CSV file using the logic-layer `add_user` function.
    """
    fields = {"USER_ID", "EMAIL", "NAME", "LASTNAME"}

    def transform_row(row):
        return {
            "user_id": row["USER_ID"].strip(),
            "email": row["EMAIL"].strip(),
            "user_name": row["NAME"].strip(),
            "user_last_name": row["LASTNAME"].strip(),
        }

    def insert_func(user_data, _table):  # passed to satisfy interface but not used
        return add_user_logic(user_data, user_data["user_id"], table=user_table)

    return load_csv_file(
        file_name, transform_row, insert_func, user_table, fields, "user"
    )


@log
def load_status_updates(file_name, user_table, status_table):
    """
    Loads status records from a CSV file using the logic-layer `add_status` function.
    """
    fields = {"STATUS_ID", "USER_ID", "STATUS_TEXT"}

    def transform_row(row):
        return {
            "status_id": row["STATUS_ID"].strip(),
            "user_id": row["USER_ID"].strip(),
            "status_text": row["STATUS_TEXT"].strip(),
        }

    def insert_func(status_data, _table):  # passed to satisfy interface but not used
        return add_status_logic(status_data, user_table, status_table)

    return load_csv_file(
        file_name, transform_row, insert_func, status_table, fields, "status"
    )


@log
def load_pictures(file_name, user_table, picture_table):
    """
    Loads picture records from a CSV file using the logic-layer `add_picture` function.
    """
    fields = {"PICTURE_ID", "USER_ID", "TAGS"}

    def transform_row(row):
        return {
            "picture_id": row["PICTURE_ID"].strip(),
            "user_id": row["USER_ID"].strip(),
            "tags": row["TAGS"].strip(),
        }

    def insert_func(picture_data, _table):  # passed to satisfy interface but not used
        return add_picture_logic(picture_data, user_table, picture_table)

    return load_csv_file(
        file_name, transform_row, insert_func, picture_table, fields, "picture"
    )


@log
def add_user(user_data, user_table):
    """
    Thin wrapper around `add_user` function
    """
    return add_user_logic(user_data, user_data["user_id"], table=user_table)


@log
def update_user(user_data, user_table):
    """
    Thin wrapper around `update_user` function
    """
    return update_user_logic(user_data, user_data["user_id"], table=user_table)


@log
def delete_user(user_id, user_table, status_table, picture_table):
    """
    Thin wrapper around `delete_user` function
    """
    return delete_user_logic(user_id, user_table, status_table, picture_table)


@log
def search_user(user_id, user_table):
    """
    Thin wrapper around `search_user` function
    """
    return search_user_logic(user_id, table=user_table)


@log
def add_status(status_data, user_table, status_table):
    """
    Thin wrapper around `add_status` function
    """
    return add_status_logic(status_data, user_table, status_table)


@log
def update_status(
    status_data, user_table, status_table
):  # pylint: disable=unused-argument
    """
    Thin wrapper around `update_status` function
    """
    status_id = status_data["status_id"]
    return update_status_logic(status_data, status_id, table=status_table)


@log
def delete_status(status_id, status_table):
    """
    Thin wrapper around `delete_status` function
    """
    return delete_status_logic(status_id, table=status_table)


@log
def search_status(status_id, status_table):
    """
    Thin wrapper around `search_status` function
    """
    return search_status_logic(status_id, table=status_table)


@log
def search_statuses_by_user(user_id, status_table):
    """
    Thin wrapper around `search_statuses by user` function
    """
    return search_statuses_by_user_logic(user_id, table=status_table)


@log
def add_picture(picture_data, user_table, picture_table):
    """
    Thin wrapper around `add_picture` function
    """
    return add_picture_logic(picture_data, user_table, picture_table)


@log
def update_picture(
    picture_data, user_table, picture_table
):  # pylint: disable=unused-argument
    """
    Thin wrapper around `update_picture` function
    """
    picture_id = picture_data["picture_id"]
    return update_picture_logic(picture_data, picture_id, table=picture_table)


@log
def delete_picture(picture_id, picture_table):
    """
    Thin wrapper around `delete_picture` function
    """
    return delete_picture_logic(picture_id, table=picture_table)


@log
def search_picture(picture_id, picture_table):
    """
    Thin wrapper around `search_picture` function
    """
    return search_picture_logic(picture_id, table=picture_table)


@log
def search_pictures_by_user(user_id, picture_table):
    """
    Thin wrapper around `search_pictures_by_user` function
    """
    return search_pictures_by_user_logic(user_id, table=picture_table)


@log
def reconcile_images_by_user(user_id, picture_table):
    """
    Identifies discrepancies between database and filesystem for a given user.
    Returns a dict with 'only_in_db' and 'only_on_disk' lists.
    """
    picture_dir = Path("picture_storage") / user_id
    db_picture_ids = set()
    disk_picture_ids = set()

    for picture in picture_table.find(user_id=user_id):
        db_picture_ids.add(picture["picture_id"])

    if picture_dir.exists():
        for pointer_file in picture_dir.rglob("*"):
            if pointer_file.is_file():
                try:
                    with pointer_file.open("r") as f:
                        content = f.read()
                        match = re.search(r"picture_id:\s*(\w+)", content)
                        if match:
                            disk_picture_ids.add(match.group(1))
                except (OSError, UnicodeDecodeError):
                    continue

    only_in_db = sorted(db_picture_ids - disk_picture_ids)
    only_on_disk = sorted(disk_picture_ids - db_picture_ids)

    return {
        "only_in_db": only_in_db,
        "only_on_disk": only_on_disk,
    }


@log
def reconcile_images(user_table, picture_table, user_id=None):
    """
    Identifies picture discrepancies between database and filesystem.
    If a user_id is passed, reconciles just for that user, else for all users
    Acts as a wrapper for reconcile_images_by_user.
    Returns a dict with {user_id: [only_in_db],[only_on_disk],}.
    """
    users_to_check = []

    if user_id:
        record = user_table.find_one(user_id=user_id)
        if not record:
            logger.warning("User {} not found. No reconciliation performed.", user_id)
            return {}
        users_to_check = [record]
    else:
        users_to_check = list(user_table.all())

    results = {}
    for user in users_to_check:
        uid = user["user_id"]
        results[uid] = reconcile_images_by_user(uid, picture_table)

    return results


@log
def batch_create_pointer_files(picture_table, user_id, picture_ids):
    """
    Function to create pointer files on disk for a given user's pictures in dB.
    :param picture_table:
    :param user_id:
    :param picture_ids:
    :return: count of successfully created pointer files
    """
    success_count = 0
    for picture_id in picture_ids:
        picture = picture_table.find_one(user_id=user_id, picture_id=picture_id)
        if picture:
            picture = safe_parse_tags(picture)
        if not picture:
            logger.debug("Picture {} not found. No pointer files created.", picture_id)
            continue
        success_check = create_pointer_file(picture)
        if not success_check:
            logger.warning(
                "Path for Picture {} not found. No pointer files created.", picture_id
            )
            continue
        if success_check:
            success_count += 1
    logger.info("Created {} pointer files for user {}.", success_count, user_id)
    return success_count
