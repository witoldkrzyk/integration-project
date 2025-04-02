"""
Integration Project (UTF-8 Converter)

This module implements a Python application that converts text files (.txt) to UTF-8
encoding. The core functionality is provided by the UTF8Converter class, which
processes files in fixed-size chunks (4KB by default) to efficiently handle large files
without consuming excessive memory. It uses an incremental decoder to attempt decoding
with UTF-8 first, and falls back to Latin-1 if needed, logging appropriate warnings.

The module supports asynchronous batch conversion of files from an input directory to
an output directory, tracking progress with tqdm. Non-.txt files found in the input
directory are moved to a separate error folder. Configuration is managed via a .env
file (which should define the absolute paths for INPUT_DIR and OUTPUT_DIR).
Detailed logging is provided to monitor key events and errors during file conversion.

This application is designed to be deployed in containerized environments using Docker,
with build and run automation facilitated by a Makefile.
"""


import os
import asyncio
import shutil
import codecs
from tqdm import tqdm
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class UTF8Converter:
    """
    A class to convert text files to UTF-8 encoding.
    """

    def __init__(self, input_path: str, output_path: str) -> None:
        """
        Initialize the converter with input and output file paths.

        Args:
            input_path (str): The path to the input file.
            output_path (str): The path to the output file.
        """

        self.input_path = input_path
        self.output_path = output_path

    def convert_file(self) -> None:
        """
        Convert the input file to UTF-8 encoding and save it to the output file.

        The file is read in 4KB chunks to efficiently handle large files.
        The method first attempts to decode using UTF-8, and if that fails,
        it falls back to Latin-1. File operations are managed with context
        managers, and key events are logged.

        Raises:
            Exception: For any errors during file reading, decoding, or writing.
        """

        logger.info(f"Starting conversion for file: {self.input_path}")

        chunk_size = 4096

        try:
            decoder = codecs.getincrementaldecoder("utf-8")()
            fallback_used = False

            with open(self.input_path, "rb") as infile, open(
                self.output_path, "w", encoding="utf-8"
            ) as outfile:
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    try:
                        decoded_chunk = decoder.decode(chunk)
                    except UnicodeDecodeError:
                        if not fallback_used:
                            logger.warning(
                                f"Failed to decode as UTF-8,"
                                f" switching to latin-1 for: {self.input_path}"
                            )
                            decoder = codecs.getincrementaldecoder("latin-1")()
                            fallback_used = True
                            decoded_chunk = decoder.decode(chunk)
                        else:
                            raise
                    outfile.write(decoded_chunk)
                outfile.write(decoder.decode(b"", final=True))

            logger.info(f"File successfully converted: {self.output_path}")
        except Exception as convert_error:
            logger.error(
                f"An error occurred while converting file "
                f"{self.input_path}: {convert_error}"
            )
            raise


async def async_convert_file(converter: UTF8Converter) -> None:
    """
    Asynchronously execute the convert_file method in a separate thread.

    Args:
        converter (UTF8Converter): An instance of UTF8Converter.
    """

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, converter.convert_file)


async def async_batch_convert(input_dir: str, output_dir: str) -> None:
    """
    Asynchronously convert all .txt files from the input directory and save the
    converted files in the output directory, while tracking progress using tqdm.
    Files that do not have a .txt extension are moved to a separate 'error_files'
    folder located in the parent directory of the input directory. If no .txt files
    are found, a warning is logged and the process exits.

    Args:
        input_dir (str): The path to the input directory containing text files.
        output_dir (str): The path to the output directory where converted files will
            be saved.

    Raises:
        Exception: Propagates any exceptions that occur during file processing.
    """

    logger.info(f"Starting batch conversion in directory: {input_dir}")

    not_txt_files = [f for f in os.listdir(input_dir) if not f.lower().endswith(".txt")]
    logger.warning(f"Found {len(not_txt_files)} NOT .txt files in input directory.")

    if not_txt_files:
        error_dir = os.path.join(os.path.dirname(input_dir), "error_files")
        os.makedirs(error_dir, exist_ok=True)

        for file in not_txt_files:
            shutil.move(os.path.join(input_dir, file), os.path.join(error_dir, file))

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(".txt")]
    if not files:
        logger.warning("No .txt files found for conversion.")
        return

    tasks = []
    for file_name in files:
        input_path = os.path.join(input_dir, file_name)
        output_path = os.path.join(output_dir, file_name)

        converter = UTF8Converter(input_path, output_path)
        tasks.append(async_convert_file(converter))

    for task in tqdm(
        asyncio.as_completed(tasks), total=len(tasks), desc="Converting files"
    ):
        await task

    logger.info("Batch conversion completed.")


if __name__ == "__main__":
    input_dir = os.getenv("INPUT_DIR")
    output_dir = os.getenv("OUTPUT_DIR")

    if not input_dir or not output_dir:
        logger.error("INPUT_DIR and OUTPUT_DIR must be set in the .env file.")
        raise EnvironmentError(
            "INPUT_DIR and OUTPUT_DIR must be set. Current values are None."
        )

    if not os.path.isdir(input_dir):
        logger.error("Input directory does not exist. Must be set in .env file")
        raise FileNotFoundError("Input directory does not exist.")

    if not os.path.isdir(output_dir):
        logger.info("Output directory does not exist. Creating directory.")
        os.makedirs(output_dir)

    asyncio.run(async_batch_convert(input_dir, output_dir))
