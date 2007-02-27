##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interfaces as Utilities Tests

$Id$
"""
__docformat__ = 'restructuredtext'

from gc import collect

import unittest

from persistent import Persistent

import transaction

from ZODB.tests.util import DB
from zodbcode.module import ManagedRegistry

from zope.interface import Interface, implements, directlyProvides
from zope.interface.interfaces import IInterface
from zope.component.interface import provideInterface
from zope.app.interface import PersistentInterface

# TODO: for some reason changing this code to use implements() does not
# work. This is due to a bug that is supposed to be fixed after X3.0.
code = """\
from zope.interface import Interface

class IFoo(Interface):
    pass

# This must be a classobj
class Foo:
    __implemented__ = IFoo

aFoo = Foo()
"""

class IQuux(Interface): pass

bar_code = """\
from zope.interface import Interface
from zope.app.interface.tests.test_interface import IQuux

class IBar(Interface): pass
class IBah(IQuux): pass
class IBaz(Interface): pass
class IBlah(IBaz): pass
"""

class Bar(Persistent): pass
class Baz(Persistent): pass

class IQux(Interface): pass

class IBarInterface(IInterface): pass

class PersistentInterfaceTest(unittest.TestCase):

    def setUp(self):

        self.db = DB()
        self.conn = self.db.open()
        self.root = self.conn.root()
        self.registry = ManagedRegistry()
        self.root["registry"] = self.registry
        transaction.commit()

    def tearDown(self):
        transaction.abort() # just in case

    def test_creation(self):
        class IFoo(PersistentInterface):
            pass

        class Foo(object):
            implements(IFoo)

        self.assert_(IFoo.providedBy(Foo()))
        self.assertEqual(IFoo._p_oid, None)

    def test_patch(self):
        self.registry.newModule("imodule", code)
        transaction.commit()
        imodule = self.registry.findModule("imodule")

        # test for a pickling bug
        self.assertEqual(imodule.Foo.__implemented__, imodule.IFoo)

        self.assert_(imodule.IFoo.providedBy(imodule.aFoo))
        # the conversion should not affect Interface
        self.assert_(imodule.Interface is Interface)

    def test_provides(self):
        """Provides are persistent."""
        
        self.registry.newModule("barmodule", bar_code)
        barmodule = self.registry.findModule("barmodule")

        bar = Bar()
        directlyProvides(bar, barmodule.IBar)
        self.root['bar'] = bar
        self.assertTrue(barmodule.IBar.providedBy(bar))

        bah = Bar()
        directlyProvides(bah, barmodule.IBah)
        self.root['bah'] = bah
        self.assertTrue(barmodule.IBah.providedBy(bah))

        blah = Bar()
        directlyProvides(blah, barmodule.IBlah)
        self.root['blah'] = blah
        self.assertTrue(barmodule.IBlah.providedBy(blah))

        transaction.commit()
        self.db.close()
        root = self.db.open().root()
        barmodule = root['registry'].findModule("barmodule")

        bar = root['bar']
        self.assertTrue(barmodule.IBar.providedBy(bar))

        bah = root['bah']
        self.assertTrue(barmodule.IBah.providedBy(bah))

        blah = root['blah']
        self.assertTrue(barmodule.IBlah.providedBy(blah))

    def test_persistentWeakref(self):
        """Verify interacton of declaration weak refs with ZODB

        Weak references to persistent objects don't remain after ZODB
        pack and garbage collection."""

        bar = self.root['bar'] = Bar()
        self.registry.newModule("barmodule", bar_code)
        barmodule = self.registry.findModule("barmodule")
        self.assertEqual(barmodule.IBar.dependents.keys(), [])
        directlyProvides(bar, barmodule.IBar)
        self.assertEqual(len(barmodule.IBar.dependents), 1)

        transaction.commit()
        del bar
        del self.root['bar']
        self.db.pack()
        transaction.commit()
        collect()

        root = self.db.open().root()
        barmodule = root['registry'].findModule("barmodule")
        self.assertEqual(barmodule.IBar.dependents.keys(), [])

    def test_persistentDeclarations(self):
        """Verify equivalency of persistent declarations

        Make sure that the persistent declaration instance are
        equivalent to the non-persistent instances they originate
        from."""

        self.registry.newModule("barmodule", bar_code)
        barmodule = self.registry.findModule("barmodule")

        class Baz(object):
            implements(barmodule.IBar)

        bar = Bar()
        directlyProvides(bar, barmodule.IBar)

        self.assertEqual(
            bar.__provides__._Provides__args,
            barmodule.IBar.dependents.keys()[0]._Provides__args
            )
        self.assertEqual(
            Baz.__implemented__.__bases__,
            barmodule.IBar.dependents.keys()[1].__bases__
            )

    def test_persistentProvides(self):
        """Verify that provideInterface works."""

        self.registry.newModule("barmodule", bar_code)
        barmodule = self.registry.findModule("barmodule")
        provideInterface('', barmodule.IBar, iface_type=IBarInterface)
        self.assertTrue(IBarInterface.providedBy(barmodule.IBar))

        self.registry.updateModule('barmodule',
                                   bar_code + '\nfoo = 1')
        barmodule = self.registry.findModule("barmodule")
        self.assertTrue(IBarInterface.providedBy(barmodule.IBar))
        
def test_suite():
    return unittest.makeSuite(PersistentInterfaceTest)
