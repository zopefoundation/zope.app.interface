##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Object Interface Vocabulary Tests

$Id: test_vocabulary.py,v 1.1 2004/04/24 23:17:36 srichter Exp $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.app.tests import setup

def test_suite():
    return DocTestSuite('zope.app.interface.vocabulary',
                        setUp=setup.placelessSetUp,
                        tearDown=setup.placelessTearDown)

if __name__ == '__main__':
    unittest.main(default='test_suite')