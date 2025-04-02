import os
import asyncio
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
        Convert the file at input_path to UTF-8 encoding and save it to output_path.

        Raises:
            ValueError: If the file extension is not .txt.
            Exception: If an error occurs during file reading, decoding, or writing.
        """

        logger.info(f"Starting conversion for file: {self.input_path}")

        if not self.input_path.lower().endswith(".txt"):
            logger.error(f"Error: Only .txt files are supported: {self.input_path}")
            raise ValueError("Only .txt files are supported")

        try:
            with open(self.input_path, "rb") as file:
                content = file.read()

            try:
                decoded_content = content.decode("utf-8")
            except UnicodeDecodeError:
                logger.warning(
                    f"Failed to decode as UTF-8, using latin-1 instead: "
                    f"{self.input_path}"
                )

                decoded_content = content.decode("latin-1")

            with open(self.output_path, "w", encoding="utf-8") as file:
                file.write(decoded_content)
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
    Asynchronously convert all .txt files from the input directory,
    saving the converted files in the output directory while tracking progress.

    Args:
        input_dir (str): The path to the input directory.
        output_dir (str): The path to the output directory.
    """

    logger.info(f"Starting batch conversion in directory: {input_dir}")

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
        logger.info("Output directory does not exist. Must be set in .env file.")
        raise FileNotFoundError("Output directory does not exist.")

    asyncio.run(async_batch_convert(input_dir, output_dir))
