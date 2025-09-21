"""
Test custom Django management commands.
"""

import io
import tempfile
from unittest.mock import patch

from psycopg import OperationalError as PsycopgError

from django.core.management import call_command, CommandError
from django.db.utils import OperationalError
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from core.models import SatisfactionSurveyResponse, User


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """
    Test commands.
    """

    def test_wait_for_db_ready(self, patched_check):
        """
        Test waiting for db when db is available.
        """

        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        Test waiting for db when getting errors.
        """

        patched_check.side_effect = [PsycopgError] * 3 + \
                                    [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 7)
        patched_check.assert_called_with(databases=['default'])


class ExportFeedbackCSVTests(TestCase):
    """
    Test the export_feedback_csv management command.
    """

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            first_name='Test',
            last_name='User'
        )

        self.survey_data = {
            'question1': 'answer1',
            'question2': {'nested': 'value'},
            'question3': ['item1', 'item2']
        }

        self.survey_response = SatisfactionSurveyResponse.objects.create(
            user=self.user,
            version='1.0',
            survey=self.survey_data
        )

    def test_export_feedback_csv_basic(self):
        """Test basic CSV export functionality."""
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            call_command('export_feedback_csv')

            output = mock_stdout.getvalue()
            self.assertIn('Exported 1 responses.', output)

            # Check CSV content
            csv_content = mock_stdout.getvalue()
            self.assertIn('response_id', csv_content)
            self.assertIn('user_id', csv_content)
            self.assertIn('user_email', csv_content)
            self.assertIn('version', csv_content)
            self.assertIn('completed_at', csv_content)

    def test_export_feedback_csv_with_filters(self):
        """Test CSV export with date and version filters."""
        # Create another response with different date
        old_date = timezone.now().replace(year=2020, month=1, day=1)
        SatisfactionSurveyResponse.objects.create(
            user=self.user,
            version='0.9',
            survey={'old_question': 'old_answer'},
            completed_at=old_date
        )

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            call_command(
                'export_feedback_csv',
                date_from='2023-01-01',
                survey_version='1.0'
            )

            output = mock_stdout.getvalue()
            self.assertIn('Exported 1 responses.', output)

    def test_export_feedback_csv_to_file(self):
        """Test CSV export to a file."""
        with tempfile.NamedTemporaryFile(
                mode='w', delete=False, suffix='.csv') as temp_file:
            temp_path = temp_file.name

        try:
            call_command('export_feedback_csv', outfile=temp_path)

            # Read the file and verify content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('response_id', content)
                self.assertIn('question1', content)
                self.assertIn('answer1', content)
        finally:
            import os
            os.unlink(temp_path)

    def test_export_feedback_csv_with_summary(self):
        """Test CSV export with summary generation."""
        with tempfile.NamedTemporaryFile(
                mode='w', delete=False, suffix='.csv') as temp_file:
            temp_path = temp_file.name

        try:
            call_command('export_feedback_csv', outfile=temp_path, summary=True)

            # Check main CSV file
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('response_id', content)

            # Check summary CSV file
            summary_path = temp_path + '.summary.csv'
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary_content = f.read()
                self.assertIn('question_key', summary_content)
                self.assertIn('answer_value', summary_content)
                self.assertIn('count', summary_content)
        finally:
            import os
            os.unlink(temp_path)
            if os.path.exists(temp_path + '.summary.csv'):
                os.unlink(temp_path + '.summary.csv')

    def test_export_feedback_csv_summary_without_outfile_error(self):
        """Test that summary option requires outfile."""
        with self.assertRaises(CommandError) as context:
            call_command('export_feedback_csv', summary=True)

        self.assertIn('--summary requires --outfile', str(context.exception))

    def test_export_feedback_csv_with_limit_keys(self):
        """Test CSV export with limited keys."""
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            call_command(
                'export_feedback_csv',
                limit_keys=['question1', 'question2.nested']
            )

            output = mock_stdout.getvalue()
            self.assertIn('Exported 1 responses.', output)
            # Should only include specified keys
            self.assertIn('question1', output)
            self.assertIn('question2.nested', output)
            # Should not include other keys
            self.assertNotIn('question3', output)

    def test_export_feedback_csv_custom_delimiter_and_encoding(self):
        """Test CSV export with custom delimiter and encoding."""
        with tempfile.NamedTemporaryFile(
                mode='w', delete=False, suffix='.csv') as temp_file:
            temp_path = temp_file.name

        try:
            call_command(
                'export_feedback_csv',
                outfile=temp_path,
                delimiter=';',
                encoding='latin-1'
            )

            # Read the file and verify delimiter
            with open(temp_path, 'r', encoding='latin-1') as f:
                content = f.read()
                # Should use semicolon as delimiter
                lines = content.split('\n')
                if len(lines) > 1:
                    self.assertIn(';', lines[0])  # Header line
        finally:
            import os
            os.unlink(temp_path)

    def test_parse_date_function(self):
        """Test the _parse_date helper function."""
        from core.management.commands.export_feedback_csv import _parse_date

        # Test with date only
        date = _parse_date('2023-01-01')
        self.assertIsNotNone(date)
        self.assertEqual(date.date().isoformat(), '2023-01-01')

        # Test with datetime
        date = _parse_date('2023-01-01T10:30:00')
        self.assertIsNotNone(date)
        self.assertEqual(date.hour, 10)
        self.assertEqual(date.minute, 30)

        # Test with end of day - the function should set time to 23:59:59
        date = _parse_date('2023-01-01', is_end=True)
        self.assertIsNotNone(date)
        # The function should set the time to end of day
        self.assertEqual(date.hour, 23)
        self.assertEqual(date.minute, 59)
        self.assertEqual(date.second, 59)

        # Test with None
        date = _parse_date(None)
        self.assertIsNone(date)

    def test_flatten_json_function(self):
        """Test the _flatten_json helper function."""
        from core.management.commands.export_feedback_csv import _flatten_json

        # Test simple dict
        data = {'key1': 'value1', 'key2': 'value2'}
        result = _flatten_json(data)
        expected = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(result, expected)

        # Test nested dict
        data = {'key1': {'nested': 'value'}}
        result = _flatten_json(data)
        expected = {'key1.nested': 'value'}
        self.assertEqual(result, expected)

        # Test with list
        data = {'key1': ['item1', 'item2']}
        result = _flatten_json(data)
        expected = {'key1': '["item1", "item2"]'}
        self.assertEqual(result, expected)

        # Test with custom separator
        data = {'key1': {'nested': 'value'}}
        result = _flatten_json(data, sep='_')
        expected = {'key1_nested': 'value'}
        self.assertEqual(result, expected)

    def test_export_feedback_csv_with_anonymous_user(self):
        """Test CSV export with anonymous user."""
        # Create anonymous user
        anonymous_user = User.objects.create_user(
            email=None,
            name='Anonymous',
            first_name='Anonymous',
            is_anonymous=True
        )

        SatisfactionSurveyResponse.objects.create(
            user=anonymous_user,
            version='1.0',
            survey={'anonymous_question': 'anonymous_answer'}
        )

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            call_command('export_feedback_csv')

            output = mock_stdout.getvalue()
            # Original + anonymous
            self.assertIn('Exported 2 responses.', output)
            self.assertIn('anonymous_question', output)

    @patch('core.management.commands.export_feedback_csv.open')
    def test_export_feedback_csv_file_write_error(self, mock_file):
        """Test handling of file write errors."""
        mock_file.side_effect = IOError("Permission denied")

        with self.assertRaises(IOError):
            call_command('export_feedback_csv', outfile='/invalid/path/file.csv')
