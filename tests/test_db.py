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

from db import ChallengeSqlDB

class TestChallengeSqlDB:

    def test_init(self, mysql_config):
        host = mysql_config['host']
        username = mysql_config['username']
        password = mysql_config['password']
        
        ChallengeSqlDB.init(host, username, password)