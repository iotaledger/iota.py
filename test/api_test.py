# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import InvalidCommand, Iota, StrictIota
from iota.adapter import MockAdapter
from iota.commands import CustomCommand
from iota.commands.core.get_node_info import GetNodeInfoCommand


class CustomCommandTestCase(TestCase):
  def setUp(self):
    super(CustomCommandTestCase, self).setUp()

    self.name     = 'helloWorld'
    self.adapter  = MockAdapter()
    self.command  = CustomCommand(self.adapter, self.name)

  def test_call(self):
    """
    Sending a custom command.
    """
    expected_response = {'message': 'Hello, IOTA!'}

    self.adapter.seed_response('helloWorld', expected_response)

    response = self.command()

    self.assertEqual(response, expected_response)
    self.assertTrue(self.command.called)

    self.assertListEqual(
      self.adapter.requests,
      [{'command': 'helloWorld'}],
    )

  def test_call_with_parameters(self):
    """
    Sending a custom command with parameters.
    """
    expected_response = {'message': 'Hello, IOTA!'}

    self.adapter.seed_response('helloWorld', expected_response)

    response = self.command(foo='bar', baz='luhrmann')

    self.assertEqual(response, expected_response)
    self.assertTrue(self.command.called)

    self.assertListEqual(
      self.adapter.requests,
      [{'command': 'helloWorld', 'foo': 'bar', 'baz': 'luhrmann'}],
    )

  def test_call_error_already_called(self):
    """
    A command can only be called once.
    """
    self.adapter.seed_response('helloWorld', {})
    self.command()

    with self.assertRaises(RuntimeError):
      self.command(extra='params')

    self.assertDictEqual(self.command.request, {'command': 'helloWorld'})

  def test_call_reset(self):
    """
    Resetting a command allows it to be called more than once.
    """
    self.adapter.seed_response('helloWorld', {'message': 'Hello, IOTA!'})
    self.command()

    self.command.reset()

    self.assertFalse(self.command.called)
    self.assertIsNone(self.command.request)
    self.assertIsNone(self.command.response)

    expected_response = {'message': 'Welcome back!'}
    self.adapter.seed_response('helloWorld', expected_response)
    response = self.command(foo='bar')

    self.assertDictEqual(response, expected_response)
    self.assertDictEqual(self.command.response, expected_response)

    self.assertDictEqual(
      self.command.request,

      {
        'command':  'helloWorld',
        'foo':      'bar',
      },
    )


class IotaApiTestCase(TestCase):
  def test_init_with_uri(self):
    """
    Passing a URI to the initializer instead of an adapter instance.
    """
    api = StrictIota('mock://')
    self.assertIsInstance(api.adapter, MockAdapter)

  def test_registered_command(self):
    """
    Preparing a documented command.
    """
    api = StrictIota(MockAdapter())

    # We just need to make sure the correct command type is
    # instantiated; individual commands have their own unit tests.
    command = api.getNodeInfo
    self.assertIsInstance(command, GetNodeInfoCommand)

  def test_unregistered_command(self):
    """
    Attempting to create an unsupported command.
    """
    api = StrictIota(MockAdapter())

    with self.assertRaises(InvalidCommand):
      # noinspection PyStatementEffect
      api.helloWorld

  def test_create_command(self):
    """
    Preparing an experimental/undocumented command.
    """
    api = StrictIota(MockAdapter())

    custom_command = api.create_command('helloWorld')

    self.assertIsInstance(custom_command, CustomCommand)
    self.assertEqual(custom_command.command, 'helloWorld')
