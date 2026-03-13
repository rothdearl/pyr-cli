import sys
import time
import unittest
from typing import Final

from pyrcli.cli.progress import ProgressBar, Spinner


class TestProgress(unittest.TestCase):
    """Test the progress modules."""
    FILES_TO_UPDATE: Final[int] = 8

    def test_progress_bar(self):
        """Test the progress bar module."""
        # With final message.
        with ProgressBar(total=self.FILES_TO_UPDATE, text_stream=sys.stderr,
                         final_message="Download complete.") as bar:
            bar.start(message="Downloading updates...")

            for file_index in range(1, self.FILES_TO_UPDATE + 1):
                time.sleep(.05)  # Simulate downloading a file.
                bar.advance(message=f"Downloaded {file_index:>2} of {self.FILES_TO_UPDATE}")

        # With message positioned to the left and show_percent = False in layout.
        with ProgressBar(total=self.FILES_TO_UPDATE, text_stream=sys.stderr, message_position="left") as bar:
            bar.layout.show_percent = False
            bar.start(message="Downloading updates...")

            for file_index in range(1, self.FILES_TO_UPDATE + 1):
                time.sleep(.05)  # Simulate downloading a file.
                bar.advance(message=f"Downloaded {file_index:>2} of {self.FILES_TO_UPDATE}")

        # With clear_on_finish = True.
        with ProgressBar(total=self.FILES_TO_UPDATE, text_stream=sys.stderr, clear_on_finish=True) as bar:
            bar.start(message="Downloading updates...")

            for file_index in range(1, self.FILES_TO_UPDATE + 1):
                time.sleep(.05)  # Simulate downloading a file.
                bar.advance(message=f"Downloaded {file_index:>2} of {self.FILES_TO_UPDATE}")

        # With final message and clear_on_finish = True.
        with ProgressBar(total=self.FILES_TO_UPDATE, text_stream=sys.stderr, final_message="Download complete.",
                         clear_on_finish=True) as bar:
            bar.start(message="Downloading updates...")

            for file_index in range(1, self.FILES_TO_UPDATE + 1):
                time.sleep(.05)  # Simulate downloading a file.
                bar.advance(message=f"Downloaded {file_index:>2} of {self.FILES_TO_UPDATE}")

        # With visible = False.
        with ProgressBar(total=self.FILES_TO_UPDATE, text_stream=sys.stderr, visible=False) as bar:
            bar.start(message="Downloading updates...")

            for file_index in range(1, self.FILES_TO_UPDATE + 1):
                time.sleep(.05)  # Simulate downloading a file.
                bar.advance(message=f"Downloaded {file_index:>2} of {self.FILES_TO_UPDATE}")

        # With total = -1.
        with ProgressBar(total=-1, text_stream=sys.stderr) as bar:
            bar.start(message="Downloading updates...")

            for file_index in range(1, self.FILES_TO_UPDATE + 1):
                time.sleep(.05)  # Simulate downloading a file.
                bar.advance(message=f"Downloaded {file_index:>2} of {self.FILES_TO_UPDATE}")

        # Manually run a progress bar.
        bar = ProgressBar(total=self.FILES_TO_UPDATE, text_stream=sys.stderr)

        bar.start(message="Downloading updates...")

        for file_index in range(1, self.FILES_TO_UPDATE + 1):
            time.sleep(.05)  # Simulate downloading a file.
            bar.advance(message=f"Downloaded {file_index:>2} of {self.FILES_TO_UPDATE}")

        bar.complete()
        bar.finalize()

        # Bar is finished, attempt to update and finalize.
        bar.update(0)
        bar.finalize()

    def test_spinner(self):
        """Test the spinner module."""
        # With final message.
        with Spinner(text_stream=sys.stderr, final_message=f"Found {self.FILES_TO_UPDATE} files to update.") as spin:
            for _ in range(self.FILES_TO_UPDATE):
                spin.advance(message="Finding files to update")
                time.sleep(0.05)  # Simulate finding a file.

        # With message positioned to the left.
        with Spinner(text_stream=sys.stderr, message_position="left") as spin:
            for _ in range(self.FILES_TO_UPDATE):
                spin.advance(message="Finding files to update")
                time.sleep(0.05)  # Simulate finding a file.

        # With visible = False.
        with Spinner(text_stream=sys.stderr, visible=False) as spin:
            for _ in range(self.FILES_TO_UPDATE):
                spin.advance(message="Finding files to update")
                time.sleep(0.05)  # Simulate finding a file.

        # Manually run a spinner.
        spin = Spinner(text_stream=sys.stderr)

        for _ in range(self.FILES_TO_UPDATE):
            spin.advance(message="Finding files to update")
            time.sleep(0.05)  # Simulate finding a file.

        spin.finalize()

        # Spinner is finished, attempt to advance.
        spin.advance()
