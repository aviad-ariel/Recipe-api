from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase

class CommandTest(TestCase):
    def test_wait_for_db_availabile(TestCase):
        """Test waiting for database when database is availabile"""
        #overwrite the behavior of __getitem__ for testing and monitor it
        with patch('django.db.utils.ConnectionHandler.__getitem__') as get_item:
            get_item.return_value = True
            call_command('wait_for_db')
            self.assertEqual(get_item.call_count, 1)

    #overwrite the behavior of time.sleep for testing with decorator
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as get_item:
            #For the first 5 time raise OperationalError, for the six's return True 
            get_item.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(get_item.call_count, 6)
