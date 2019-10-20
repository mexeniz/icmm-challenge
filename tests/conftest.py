# -*- coding: utf-8 -*-

import pytest
import os
import sys
import inspect
CURRENT_DIR = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
# Include paths for module search
sys.path.insert(0, PARENT_DIR)


@pytest.fixture(scope='session')
def mysql_config():
    return {
        'host': 'localhost',
        'username': 'root',
        'password': 'password'
    }