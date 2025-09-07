"""
Helper functions for validating data objects
"""

import os
import re
from ast import literal_eval
from loguru import logger
from email_validator import validate_email, EmailNotValidError
from social_network.logging_decorator import log_decorator as log


ATTRIBUTE_MAX_LENGTHS = {
    "user_id": 32,
    "email": 100,
    "user_name": 30,
    "user_last_name": 100,
    "status_id": 32,
    "status_text": 140,
    "picture_id": 32,
    "tags": 100,
}

VALID_NAME_PATTERN = r"^[a-zA-Z0-9_]+$"


@log
def attribute_length_validator(string, attribute):
    """
    Validates that the string does not exceed the maximum allowed length for the attribute.

    :param string: The input value to validate.
    :param attribute: The attribute key to check the max length for.
    :return: True if the string is within the allowed length, False otherwise.
    """
    max_length = ATTRIBUTE_MAX_LENGTHS.get(attribute)
    if max_length is None:
        logger.warning("Unknown attribute {} passed to validator.", attribute)
        return False

    if len(string) <= max_length:
        logger.info(
            "Attribute length validation passed. String: {}, Attribute: {}, Max length: {}",
            string,
            attribute,
            max_length,
        )
        return True

    logger.debug(
        "Attribute length validation failed. String: {}, Attribute: {}, Max length: {}",
        string,
        attribute,
        max_length,
    )
    return False


@log
def valid_name_format(value):
    """
    Checks that a value only contains alphanumeric characters and underscores.
    """
    value = value.strip()

    if not isinstance(value, str):
        logger.warning("Valid name check failed: not a string")
        return False
    if not re.fullmatch(VALID_NAME_PATTERN, value):
        logger.debug("Valid name check failed: contains invalid characters")
        return False
    return True


@log
def file_name_validator(file_name):
    """
    Validates that a file exists and has a valid basename format.

    Checks if the file exists on disk, has a valid name format (alphanumeric/underscores),
    and that the name is of reasonable length.

    :param file_name: Full path or name of the file.
    :return: True if the file passes all validation checks, False otherwise.
    """
    file_name = file_name.strip()

    if not os.path.isfile(file_name):
        logger.debug("Filename validation failed: file does not exist")
        return False

    base_name = os.path.splitext(os.path.basename(file_name))[0]
    if not valid_name_format(base_name):
        logger.debug("Filename validation failed: invalid characters in basename")
        return False

    if len(base_name) < 3:
        logger.debug("Filename validation failed: basename too short")
        return False

    logger.info("Filename validation passed")
    return True


@log
def csv_extension_validator(file_name):
    """
    boolean check if a csv file has a valid extension
    """
    file_name = file_name.strip()

    if not file_name.lower().endswith(".csv"):
        logger.debug(
            "CSV extension validation failed due to file_name not ending with .csv"
        )
        return False

    logger.info("CSV extension validation passed")
    return True


@log
def picture_extension_validator(file_name):
    """
    boolean check if a picture file has a valid extension
    """
    file_name = file_name.strip()

    if not file_name.lower().endswith(".png"):
        logger.debug(
            "Picture extension validation failed due to file_name not ending with .png"
        )
        return False

    logger.info("Picture extension validation passed")
    return True


@log
def string_validator(string):
    """
    boolean check if a string is valid
    """
    if not string or not isinstance(string, str) or not string.strip():
        logger.debug(
            "String validation failed due to object passed in being NULL or whitespace-only"
        )
        return False

    logger.info("String validation passed {}", string)
    return True


@log
def user_email_validator(email):
    """
    boolean check if a user email is valid
    """
    if not isinstance(email, str):
        logger.warning("Invalid email {}: Not a string", email)
        return False

    try:
        validate_email(email, check_deliverability=False)
        logger.info("Email {} is valid", email)
        return True
    except EmailNotValidError as error:
        logger.info("Invalid email {}: {}", email, error)
        return False


FILENAME_VALIDATORS = {
    "csv_file": (file_name_validator, csv_extension_validator),
    "picture_file": (file_name_validator, picture_extension_validator),
}


@log
def tag_normalizer(tags):
    """
    Function to normalize tag string into an ordered list suitable for defining a file hierarchy
    Returns the normalized list of tags for file hierarchy creation/navigation
    """
    raw_tags = tags.split("#")
    unique_tags = {tag.strip() for tag in raw_tags if tag.strip()}
    normalized_tags = sorted(
        [tag for tag in unique_tags if re.fullmatch(VALID_NAME_PATTERN, tag)]
    )

    if not normalized_tags:
        logger.debug("No valid tags found")
        return []
    return normalized_tags


@log
def safe_parse_tags(picture):
    """
    Attempts to safely convert the 'tags' field from a stringified list into a real list.
    If parsing fails, sets the tags field to an empty list.

    :param picture: Dictionary containing a 'tags' key.
    :return: The same dictionary, with the 'tags' value updated to a list.
    """
    tags = picture.get("tags")
    if isinstance(tags, str):
        try:
            tags = literal_eval(tags)
        except (ValueError, SyntaxError):
            logger.warning("Failed to parse tags string: {}", tags)
            tags = []
    picture["tags"] = tags
    return picture
