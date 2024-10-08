import json
import unittest
import sys
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Type

ExcInfo = tuple[Type[BaseException], BaseException, TracebackType | None]
OptExcInfo = ExcInfo | None


def add_path() -> None:
    """
    Add the project directory to the system path.
    """
    path = Path(__file__).parents[1]
    sys.path.append(str(path))


class JSONTestResult(unittest.TestResult):
    """
    A test result class that can be used with JSONTestRunner.
    It stores the results of the tests in a list of dictionaries.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Constructor method for `JSONTestResult`.
        """
        super().__init__(*args, **kwargs)
        self.results = []
        self.counter = {
            "success": 0,
            "errors": 0,
            "failures": 0,
            "skipped": 0,
        }

    def addSuccess(self, test: unittest.TestCase) -> None:
        """
        Add a successful test to the results.

        Parameters
        ----------
        test : unittest.TestCase
            The test case.
        """
        self.results.append({"test": str(test), "outcome": "success"})
        self.counter["success"] += 1

    def addError(self, test: unittest.TestCase, err: OptExcInfo) -> None:
        """
        Add an error to the results.

        Parameters
        ----------
        test : unittest.TestCase
            The test case.

        err : OptExcInfo
            The error information.
        """
        self.results.append(
            {"test": str(test), "outcome": "error", "error": self._exc_info_to_string(err, test)}
        )
        self.counter["errors"] += 1

    def addFailure(self, test: unittest.TestCase, err: OptExcInfo) -> None:
        """
        Add a failure to the results.

        Parameters
        ----------
        test : unittest.TestCase
            The test case.

        err : OptExcInfo
            The error information.
        """
        self.results.append(
            {"test": str(test), "outcome": "failure", "error": self._exc_info_to_string(err, test)}
        )
        self.counter["failures"] += 1

    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        """
        Add a skipped test to the results.

        Parameters
        ----------
        test : unittest.TestCase
            The test case.

        reason : str
            The reason for skipping the test.
        """
        self.results.append({"test": str(test), "outcome": "skipped", "reason": reason})
        self.counter["skipped"] += 1


class JSONTestRunner(unittest.TextTestRunner):
    """
    A test runner class that can be used with JSONTestResult.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Constructor method for `JSONTestRunner`.
        """
        super().__init__(*args, **kwargs)

    def run(self, test: unittest.TestSuite | unittest.TestCase, name: str) -> None:
        """
        Run the test suite/case and save the results to a JSON file.

        Parameters
        ----------
        test : unittest.TestSuite | unittest.TestCase
            The test suite/case to run.

        name : str
            The name of the test for creating the JSON file.
        """
        result = JSONTestResult()
        test(result)

        result = {
            "stats": {
                "total": result.testsRun,
                "success": result.counter["success"],
                "errors": result.counter["errors"],
                "failures": result.counter["failures"],
                "skipped": result.counter["skipped"],
            },
            "results": result.results,
        }

        path = (
            Path(__file__).parent / "results" / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        )
        with open(path, "w") as file:
            file.write(json.dumps(result, indent=4))
