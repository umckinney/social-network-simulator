"""
Provides a basic frontend
"""

import sys
from loguru import logger
import social_network.main as main
from social_network.validators import (
    attribute_length_validator,
    ATTRIBUTE_MAX_LENGTHS,
    string_validator,
    user_email_validator,
    FILENAME_VALIDATORS,
    safe_parse_tags,
)
from social_network.logging_decorator import log_decorator as log

logger.remove()

LOG_LEVEL_FILE = "DEBUG"
LOG_LEVEL_CONSOLE = "INFO"
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | "
    "<level>{level: <8}</level> | "
    "<yellow>Line {line: >4} ({file}):</yellow> <b>{message}</b>"
)
logger.add(
    "file.log",
    level=LOG_LEVEL_FILE,
    format=LOG_FORMAT,
    colorize=False,
    backtrace=True,
    diagnose=True,
)
logger.add(sys.stderr, level=LOG_LEVEL_CONSOLE, format=LOG_FORMAT)

USER_PROMPTS = {
    "user_id": "User ID",
    "email": "User Email",
    "user_name": "User Name",
    "user_last_name": "User Last Name",
}

USER_VALIDATORS = {
    "email": user_email_validator,
}

STATUS_PROMPTS = {
    "status_id": "Status ID",
    "user_id": "User ID",
    "status_text": "Status Text",
}

PICTURE_PROMPTS = {
    "user_id": "User ID",
    "tags": "Tags (start each with # and separated by a space)",
}


@log
def validated_input_collector(prompt_dict, validators_dict=None):
    """
    Returns a function that collects user input for a pre-defined set of fields
    Handles field-level validation of user input
    Validators return True if valid, False otherwise
    """

    def collect_inputs():
        inputs = {}
        for field, prompt in prompt_dict.items():
            value = input(f"{prompt} >> ").strip()

            if not string_validator(value):
                print(f"{field} is invalid (empty or not a string). Try again.")
                return None

            if validators_dict:
                field_validator = validators_dict.get(field)
                if field_validator and not field_validator(value):
                    print(f"{field} failed validation. Try again.")
                    return None

            if field in ATTRIBUTE_MAX_LENGTHS and not attribute_length_validator(
                value, field
            ):
                print(f"{field} exceeds allowed length. Try again.")
                return None

            inputs[field] = value
        return inputs

    return collect_inputs


@log
def get_user_input():
    """
    Helper method for getting user input
    """
    return validated_input_collector(USER_PROMPTS, USER_VALIDATORS)()


@log
def get_status_input():
    """
    Helper method for getting status input
    """
    return validated_input_collector(STATUS_PROMPTS)()


@log
def get_picture_input():
    """
    Helper method for getting picture input
    """
    return validated_input_collector(PICTURE_PROMPTS)()


@log
def load_data_file(table, loader_func, file_type, table2=None):
    """
    Generic function that loads data from a file
    """
    prompt_dict = {"filename": f"Enter the name of the {file_type} file "}
    user_input = validated_input_collector(prompt_dict, FILENAME_VALIDATORS)()

    if not user_input or "filename" not in user_input:
        print("No file name entered. Returning to main menu.")
        return False

    filename = user_input["filename"]
    if table2:
        results = loader_func(filename, table2, table)
    else:
        results = loader_func(filename, table)

    if not results:
        logger.info(f"Something went wrong loading the {file_type} file.")
        print(f"Something went wrong loading the {file_type} file.")
        return False
    logger.debug(f"{filename} loaded as {file_type} file")
    print(f"{filename} loaded as {file_type} file")
    return True


@log
def load_users(table):
    """
    Loads user accounts from a file - calls load_data_file
    """
    return load_data_file(table, main.load_users, "user")


@log
def load_status_updates(user_table, status_table):
    """
    Loads status updates from a file - calls load_data_file
    """
    return load_data_file(
        status_table, main.load_status_updates, "status update", user_table
    )


@log
def load_pictures(user_table, picture_table):
    """
    Loads pictures from a file - calls load_data_file
    """
    return load_data_file(
        picture_table, main.load_pictures, "picture update", user_table
    )


@log
def handle_add_user(table):
    """
    Adds a new user into the database
    """
    user_data = get_user_input()
    if not user_data:
        print("User input invalid or cancelled. Operation aborted.")
        return False
    result = main.add_user(user_data, table)
    if result:
        print(f"User {user_data['user_id']} added successfully!")
    else:
        print(f"Unable to add user {user_data['user_id']}.")
    return result


@log
def handle_update_user(table):
    """
    Updates an existing user in the database
    """
    user_data = get_user_input()
    if not user_data:
        print("User input invalid or cancelled. Operation aborted.")
        return False
    result = main.update_user(user_data, table)
    if result:
        print(f"User {user_data['user_id']} updated successfully!")
    else:
        print(f"Unable to update user {user_data['user_id']}.")
    return result


@log
def handle_search_user(table):
    """
    Searches a user in the database
    """
    prompt_dict = {"user_id": "Enter a User ID to search "}
    user_data = validated_input_collector(prompt_dict)()
    if not user_data:
        print("Search cancelled or invalid input.")
        return False
    user_id = user_data["user_id"]
    result = main.search_user(user_id, table)
    if result:
        print("User found!")
        print(f"User ID     | {result['user_id']}")
        print(f"Email       | {result['email']}")
        print(f"User Name   | {result['user_name']}")
        print(f"Last Name   | {result['user_last_name']}")
        return result
    print(f"Unable to find user {user_id}.")
    return False


@log
def handle_delete_user(user_table, status_table, picture_table):
    """
    Deletes user from the database
    """
    prompt_dict = {"user_id": "Enter a User ID to delete "}
    user_data = validated_input_collector(prompt_dict)()
    if not user_data:
        print("Search cancelled or invalid input.")
        return False
    user_id = user_data["user_id"]
    status_deletion_result = main.delete_user(
        user_id, user_table, status_table, picture_table
    )
    if status_deletion_result:
        print(f"User {user_data['user_id']} deleted successfully!")
        return True
    print(f"Unable to delete user {user_data['user_id']}.")
    return False


@log
def handle_add_status(user_table, status_table):
    """
    Adds a new status into the database
    """
    status_data = get_status_input()
    if not status_data:
        print("Status input invalid or cancelled. Operation aborted.")
        return False
    result = main.add_status(status_data, user_table, status_table)
    if result:
        print(f"Status {status_data['status_id']} added successfully!")
    else:
        print(f"Unable to add status {status_data['status_id']}.")
    return result


@log
def handle_update_status(user_table, status_table):
    """
    Updates information for an existing status
    """
    status_data = get_status_input()
    if not status_data:
        print("Status input invalid or cancelled. Operation aborted.")
        return False
    result = main.update_status(status_data, user_table, status_table)
    if result:
        print(f"Status {status_data['status_id']} updated successfully!")
    else:
        print(f"Unable to update status {status_data['status_id']}.")
    return result


@log
def handle_search_status(status_table):
    """
    Searches a status in the database
    """
    prompt_dict = {"status_id": "Enter a Status ID to search "}
    status_data = validated_input_collector(prompt_dict)()
    if not status_data:
        print("Search cancelled or invalid input.")
        return False
    status_id = status_data["status_id"]
    result = main.search_status(status_id, status_table)
    if result:
        print("Status found!")
        print(f"Status ID   | {result['status_id']}")
        print(f"User ID     | {result['user_id']}")
        print(f"Status Text | {result['status_text']}")
        return result
    print(f"Unable to find status {status_id}.")
    return False


@log
def handle_delete_status(status_table):
    """
    Deletes status from the database
    """
    prompt_dict = {"status_id": "Enter a Status ID to delete "}
    status_data = validated_input_collector(prompt_dict)()
    if not status_data:
        print("Search cancelled or invalid input.")
        return False
    status_id = status_data["status_id"]
    result = main.delete_status(status_id, status_table)
    if result:
        print(f"Status {status_data['status_id']} deleted successfully!")
        return True
    print(f"Unable to delete status {status_data['status_id']}.")
    return False


@log
def handle_add_picture(user_table, picture_table):
    """
    Adds a new picture into the database
    """
    picture_data = get_picture_input()
    if not picture_data:
        print("Picture input invalid or cancelled. Operation aborted.")
        return False
    result = main.add_picture(picture_data, user_table, picture_table)
    if result:
        print(f"Picture {picture_data['picture_id']} added successfully!")
    else:
        print(f"Unable to add picture {picture_data['picture_id']}.")
    return result


@log
def handle_list_pictures_by_user(picture_table):
    """
    Searches for all pictures associated with a user_id
    """
    prompt_dict = {"user_id": "Enter a User ID to search "}
    picture_data = validated_input_collector(prompt_dict)()
    if not picture_data:
        print("Search cancelled or invalid input.")
        return False

    user_id = picture_data["user_id"]
    pictures = main.search_pictures_by_user(user_id, picture_table)
    if not pictures:
        print(f"No pictures found for user {user_id}.")
        return False

    count_width = 8
    picture_id_width = 32
    tags_width = 100

    header = (
        f"{'Count'.ljust(count_width)} | "
        f"{'Picture ID'.ljust(picture_id_width)} | "
        f"{'Tags'.ljust(tags_width)}"
    )
    divider = "-" * (count_width + picture_id_width + tags_width + 6)
    print(header)
    print(divider)

    for i, picture in enumerate(pictures, start=1):
        if picture:
            picture = safe_parse_tags(picture)
        tag_string = (
            " ".join(picture["tags"])
            if isinstance(picture["tags"], list)
            else str(picture["tags"])
        )
        print(
            f"{str(i).ljust(count_width)} | "
            f"{picture['picture_id'].ljust(picture_id_width)} | "
            f"{tag_string.ljust(tags_width)}"
        )
    return True


@log
def handle_reconcile_images(user_table, picture_table):
    """
    Compares the database records and the on-disk files for pictures.
    If a user_id is provided, checks that user.
    If a user_id is not provided, checks all users.
    Calls display_reconciliation_results to reports discrepancies.
    """
    prompt_dict = {
        "user_id": "Enter a User ID to reconcile or leave blank to check all users "
    }
    input_data = validated_input_collector(prompt_dict)()
    if not input_data or not input_data.get("user_id"):
        user_id = None
        logger.info("Reconciling all users")
    else:
        user_id = input_data["user_id"]
        logger.info("Reconciling for user {}", user_id)

    results = main.reconcile_images(user_table, picture_table, user_id)
    if not results:
        logger.warning("RECONCILIATION ABORTED: No record of user {} in dB.", user_id)
        return False

    display_reconciliation_results(results)
    prompt_dict = {"reconcile": 'Enter "Y" to create a pointer file for these results.'}
    reconcile_data = validated_input_collector(prompt_dict)()
    if reconcile_data and reconcile_data.get("reconcile", "").lower() == "y":
        success_count = 0
        for uid, discrepancies in results.items():
            picture_ids = discrepancies["only_in_db"]
            success_count += main.batch_create_pointer_files(
                picture_table, uid, picture_ids
            )

        print(
            f"Successfully created {success_count} pointer files for {len(results)} users."
        )

    return True


@log
def display_reconciliation_results(results):
    """
    Nicely formats and prints the reconciliation results.
    """
    for user_id, result in results.items():
        only_in_db = result.get("only_in_db", [])
        only_on_disk = result.get("only_on_disk", [])

        print("-" * 50)
        print(f"\nReconciliation results for user: {user_id}")
        print("-" * 50)
        print("\nPictures listed in database but missing on disk:")
        print("-" * 50)
        if only_in_db:
            for pic_id in only_in_db:
                print(f"- {pic_id}")
        else:
            print("None missing on disk")

        print("-" * 50)
        print("\nPictures found on disk but missing in database:")
        print("-" * 50)
        if only_on_disk:
            for pic_id in only_on_disk:
                print(f"- {pic_id}")
        else:
            print("None missing in database")


@log
def quit_program():
    """
    Quits program
    """
    sys.exit()


@log
def run_program():
    """
    Runs the program
    """
    user_db, status_db, picture_db = main.initialize_db()
    menu_options = {
        "A": lambda: load_users(user_db),
        "B": lambda: load_status_updates(user_db, status_db),
        "C": lambda: handle_add_user(user_db),
        "D": lambda: handle_update_user(user_db),
        "E": lambda: handle_search_user(user_db),
        "F": lambda: handle_delete_user(user_db, status_db, picture_db),
        "G": lambda: handle_add_status(user_db, status_db),
        "H": lambda: handle_update_status(user_db, status_db),
        "I": lambda: handle_search_status(status_db),
        "J": lambda: handle_delete_status(status_db),
        "K": lambda: handle_add_picture(user_db, picture_db),
        "L": lambda: handle_list_pictures_by_user(picture_db),
        "M": lambda: handle_reconcile_images(user_db, picture_db),
        "Q": quit_program,
    }
    while True:
        user_selection = input(
            """
                            A: Load user database
                            B: Load status database
                            C: Add user
                            D: Update user
                            E: Search user
                            F: Delete user
                            G: Add status
                            H: Update status
                            I: Search status
                            J: Delete status
                            K: Add picture
                            L: List pictures by user
                            M: Reconcile pictures
                            Q: Quit

                            Please enter your choice: """
        )
        user_selection = user_selection.upper()
        if user_selection in menu_options:
            menu_options[user_selection]()
        else:
            print("That is not a valid option. Please select again.")


if __name__ == "__main__":
    run_program()
