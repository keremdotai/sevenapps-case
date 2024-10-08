import argparse
import os
import subprocess
import shutil
from pathlib import Path

from dotenv import load_dotenv


def setup() -> None:
    """
    Set up the environment variables before running the tests.
    Moreover, it creates the results directory if it does not exist.
    """
    # Load the environment variables
    env_path = Path(__file__).parents[2] / ".env"
    load_dotenv(env_path)
    os.environ["DEV_MODE"] = "true"

    if not (Path(__file__).parent / "results").exists():
        os.makedirs(Path(__file__).parent / "results", mode=0o777)


def remove_pycache() -> None:
    """
    This function removes the __pycache__ directories in the project.
    """
    root = Path(__file__).parents[1]
    for path in root.rglob("__pycache__"):
        shutil.rmtree(path)

    path = Path(__file__).parent / "user.json"
    if path.exists():
        os.remove(path)


if __name__ == "__main__":
    # Get list of all test files
    paths = sorted([path for path in Path(__file__).parent.glob("test_*.py")])
    choices = ["_".join(path.stem.split("_")[2:]) for path in paths]

    # Parse arguments
    parser = argparse.ArgumentParser(description="Run the tests.")
    parser.add_argument(
        "tests", help=f"The test/s to run. It should be one of the choices: {', '.join(choices)}", nargs="*"
    )
    parser.add_argument("--all", action=argparse.BooleanOptionalAction, help="Run all tests.")
    args = parser.parse_args()

    # Set up the environment variables
    setup()

    # Run all tests
    processes: list[subprocess.Popen] = []

    if args.all:
        for path in paths:
            process = subprocess.Popen(
                ["python", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            processes.append(process)
    else:
        for test in args.tests:
            if test not in choices:
                raise ValueError(f"Invalid test: {test}")

            index = choices.index(test)
            process = subprocess.Popen(
                ["python", str(paths[index])],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            processes.append(process)

    # Wait for all processes to finish
    for process in processes:
        process.wait()

    # Remove the __pycache__ directories
    remove_pycache()

    # Print the final message
    print("Tests are performed.")
