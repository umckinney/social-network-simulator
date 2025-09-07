"""
Handles file structure operations for picture records.

Responsibilities:
- Ensures correct folder hierarchy based on user ID and picture tags.
- Automatically creates directories and pointer files as needed.
- Encodes folder nesting from tags, using the first tag as the first subfolder, and so on.
- If tags are missing, the picture is placed directly in the user’s folder.

Folder Logic:
- Parent folder: Named after `user_id`.
- Nested subfolders: Created from `tags` (if present).
- Pointer file: Created with a filename based on the record's database `id`.

This module is future-proofed for eventual integration with actual image file handling.
"""

from pathlib import Path
from loguru import logger
from social_network.logging_decorator import log_decorator as log
from social_network.validators import safe_parse_tags


@log
def get_path(record):
    """
    Constructs a full directory path for a picture record using its tags and user ID.

    The path starts with a base directory (`picture_storage/`) followed by the user ID,
    and then any subfolders derived from the tag list.

    Returns:
        Path object pointing to the appropriate directory.
        None if required keys are missing from the record.
    """
    try:
        user_id = record["user_id"]
        picture_id = record["picture_id"]
        record = safe_parse_tags(record)
        folders = record["tags"]

        if not folders:
            logger.info("No folders found in record: {}", picture_id)
            return Path("picture_storage") / user_id

        base_dir = Path("picture_storage") / user_id
        full_path = base_dir.joinpath(*folders)

        logger.info("Generated path for picture {}: {}", picture_id, full_path)
        return full_path

    except KeyError as error:
        logger.error("Missing expected key in record: {}", error)
        return None


@log
def create_pointer_file(record):
    """
    Creates a pointer file representing a picture record in the appropriate folder.

    This simulates image file placement using a `.txt` file. The file is named based
    on the auto-incremented database `id`, padded to 10 digits.

    Returns:
        True on successful file creation.
        False on failure (invalid input, missing folder, permission error).
    """
    try:
        numeric_id = int(record["id"])
        file_name = f"{numeric_id:010}.txt"
    except (KeyError, ValueError, TypeError):
        logger.warning(
            "Skipping pointer file: missing or invalid 'id' for picture record {}",
            record.get("picture_id", "UNKNOWN"),
        )
        return False

    full_path = get_path(record)
    try:
        full_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        logger.error("Permission error while creating folder {}", full_path)
        return False
    except OSError:
        logger.error("OS Error while creating folder {}", full_path)
        return False

    file_path = full_path / file_name

    try:
        file_path.write_text(
            (
                f"Pointer file for picture_id: {record['picture_id']}\n"
                f"User ID: {record['user_id']}\n"
                f"Tags: {record['tags']}"
            )
        )
        logger.info("Pointer file created at {}", file_path)
        return True
    except PermissionError:
        logger.error("Permission denied while writing to file: {}", file_path)
        return False
    except OSError as error:
        logger.error("OS error during file writing: {}", error)
        return False
