from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota, AsyncIota, TransactionHash, TryteString
from iota.adapter import MockAdapter, async_return
from iota.commands.extended.get_latest_inclusion import \
  GetLatestInclusionCommand
from iota.filters import Trytes
from test import patch, MagicMock, async_test


class GetLatestInclusionRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetLatestInclusionCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetLatestInclusionRequestFilterTestCase, self).setUp()

    self.hash1 = (
      'TESTVALUE9DONTUSEINPRODUCTION99999DXSCAD'
      'YBVDCTTBLHFYQATFZPYPCBG9FOUKIGMYIGLHM9NEZ'
    )

    self.hash2 = (
      'TESTVALUE9DONTUSEINPRODUCTION99999EMFYSM'
      'HWODIAPUTTFDLQRLYIDAUIPJXXEXZZSBVKZEBWGAN'
    )

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      # Raw trytes are extracted to match the IRI's JSON protocol.
      'hashes': [self.hash1, self.hash2],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_compatible_types(self):
    """
    Request contains values that can be converted to the expected
    types.
    """
    filter_ = self._filter({
      'hashes': [
        # Any TrytesCompatible value can be used here.
        TransactionHash(self.hash1),
        bytearray(self.hash2.encode('ascii')),
      ],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        # Raw trytes are extracted to match the IRI's JSON protocol.
        'hashes': [self.hash1, self.hash2],
      },
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'hashes': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'hashes': [TransactionHash(self.hash1)],

        # Uh, before we dock, I think we ought to discuss the bonus
        # situation.
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_hashes_null(self):
    """
    ``hashes`` is null.
    """
    self.assertFilterErrors(
      {
        'hashes': None,
      },

      {
        'hashes': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_hashes_wrong_type(self):
    """
    ``hashes`` is not an array.
    """
    self.assertFilterErrors(
      {
        # It's gotta be an array, even if there's only one hash.
        'hashes': TransactionHash(self.hash1),
      },

      {
        'hashes': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_hashes_empty(self):
    """
    ``hashes`` is an array, but it is empty.
    """
    self.assertFilterErrors(
      {
        'hashes': [],
      },

      {
        'hashes': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_hashes_contents_invalid(self):
    """
    ``hashes`` is a non-empty array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'hashes': [
          b'',
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          #   filter isn't cheating!
          TryteString(self.hash1),

          2130706433,
          b'9' * 82,
        ],
      },

      {
        'hashes.0':  [f.Required.CODE_EMPTY],
        'hashes.1':  [f.Type.CODE_WRONG_TYPE],
        'hashes.2':  [f.Required.CODE_EMPTY],
        'hashes.3':  [Trytes.CODE_NOT_TRYTES],
        'hashes.5':  [f.Type.CODE_WRONG_TYPE],
        'hashes.6':  [Trytes.CODE_WRONG_FORMAT],
      },
    )


class GetLatestInclusionCommandTestCase(TestCase):
  def setUp(self):
    super(GetLatestInclusionCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = GetLatestInclusionCommand(self.adapter)

    # Define some tryte sequences that we can re-use across tests.
    self.milestone =\
      TransactionHash(
        b'TESTVALUE9DONTUSEINPRODUCTION99999W9KDIH'
        b'BALAYAFCADIDU9HCXDKIXEYDNFRAKHN9IEIDZFWGJ'
      )

    self.hash1 =\
      TransactionHash(
        b'TESTVALUE9DONTUSEINPRODUCTION99999TBPDM9'
        b'ADFAWCKCSFUALFGETFIFG9UHIEFE9AYESEHDUBDDF'
      )

    self.hash2 =\
      TransactionHash(
        b'TESTVALUE9DONTUSEINPRODUCTION99999CIGCCF'
        b'KIUFZF9EP9YEYGQAIEXDTEAAUGAEWBBASHYCWBHDX'
      )

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.extended.get_latest_inclusion.GetLatestInclusionCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      # Don't need to call with proper args here.
      response = api.get_latest_inclusion('hashes')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  @async_test
  async def test_wireup_async(self):
    """
    Verify that the command is wired up correctly. (async)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.extended.get_latest_inclusion.GetLatestInclusionCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      # Don't need to call with proper args here.
      response = await api.get_latest_inclusion('hashes')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  @async_test
  async def test_happy_path(self):
    """
    Successfully requesting latest inclusion state.
    """
    self.adapter.seed_response('getNodeInfo', {
        # ``getNodeInfo`` returns lots of info, but the only value that
        # matters for this test is ``latestSolidSubtangleMilestone``.
        'latestSolidSubtangleMilestone': self.milestone,
      },
    )

    self.adapter.seed_response('getInclusionStates', {
      'states': [True, False],
    })

    response = await self.command(hashes=[self.hash1, self.hash2])

    self.assertDictEqual(
      response,

      {
        'states': {
          self.hash1: True,
          self.hash2: False,
        },
      }
    )
