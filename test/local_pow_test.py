from iota import Iota, TryteString, TransactionHash, TransactionTrytes, \
    HttpAdapter, MockAdapter
from iota.adapter.wrappers import RoutingWrapper
from unittest import TestCase
import sys
from unittest.mock import MagicMock, patch

# Load mocked package on import from pow pkg.
# Therefore we can test without having to install it.
sys.modules['pow'] = MagicMock()

class LocalPowTestCase(TestCase):
    """
    Unit tests for `local_pow` feature using `pow` package
    from `ccurl.inteface.py`.
    """
    # We are only interested in if the ccurl interface is called.
    # Don't care about the values, and there is no actual PoW
    # calculation in these tests. Testing the functional correctness
    # of the PoW calculation is done in iotaledger/ccurl.interface.py.
    # Filters are thoroughly tested in `attach_to_tangle_test.py`.
    def setUp(self):
        """
        These values will be used in the tests. 
        """
        # Will be padded to transaction length by TransactionTrytes()
        self.trytes1 ='CCLDVADBEACCWCTCEAZBCDFCE'
        # Will be padded to transaction length by TransactionTrytes()
        self.trytes2 ='CGDEAHDFDPCBDGDPCRCHDXCCDBDEAKDPC'
        # Will be padded to hash length by TransactionHash()
        self.trunk ='EWSQPV9AGXUQRYAZIUONVBXFNWRWIGVCFT'
        self.branch ='W9VELHQPPERYSG9ZLLAHQKDLJQBKYYZOS'
        self.mwm = 14

        # Create real objects so that we pass the filters
        self.bundle = [TransactionTrytes(self.trytes1), TransactionTrytes(self.trytes2)]
        # ccurl_bundle is only needed to differentiate between response
        # from mocked pow and MockAdapter in some test cases.
        self.ccurl_bundle = [TransactionTrytes(self.trytes1)]
        self.trunk = TransactionHash(self.trunk)
        self.branch = TransactionHash(self.branch)
    
    def test_backward_compatibility(self):
        """
        Test that the local_pow feature is backward compatible.
        That is, if `local_pow` argument is omitted, it takes no
        effect and the pow extension package is not called.
        """
        with patch('pow.ccurl_interface.attach_to_tangle',
                   MagicMock(return_value=self.ccurl_bundle)) as mocked_ccurl:
            self.adapter = MockAdapter()
            self.adapter.seed_response('attachToTangle',{
                'trytes': self.bundle,
            })
            # No `local_pow` argument is passed to the api!
            api = Iota(self.adapter)
            result = api.attach_to_tangle(
                self.trunk,
                self.branch,
                self.bundle,
                self.mwm)
            # Ccurl interface was not called
            self.assertFalse(mocked_ccurl.called)
            # Result is the one returned by MockAdapter
            self.assertEqual(result['trytes'], self.bundle)
            # And not by mocked pow pkg
            self.assertNotEqual(result['trytes'], self.ccurl_bundle)

    def test_http_adapter(self):
        """
        Test if local_pow feature works with HttpAdapter.
        """
        # Note that we need correct return value to pass the
        # response filter.
        with patch('pow.ccurl_interface.attach_to_tangle',
                    MagicMock(return_value=self.bundle)) as mocked_ccurl:
            api = Iota(HttpAdapter('http://localhost:14265/'),local_pow=True)
            result = api.attach_to_tangle(
                self.trunk,
                self.branch,
                self.bundle,
                self.mwm)
            self.assertTrue(mocked_ccurl.called)
            self.assertEqual(result['trytes'], self.bundle)

    def test_mock_adapter(self):
        """
        Test if local_pow feature works with MockAdapter.
        """
        # Note that we need correct return value to pass the
        # response filter.
        with patch('pow.ccurl_interface.attach_to_tangle',
                    MagicMock(return_value=self.bundle)) as mocked_ccurl:
            api = Iota(MockAdapter(),local_pow=True)
            result = api.attach_to_tangle(
                self.trunk,
                self.branch,
                self.bundle,
                self.mwm)
            self.assertTrue(mocked_ccurl.called)
            self.assertEqual(result['trytes'], self.bundle)
    
    def test_routing_wrapper(self):
        """
        Test if local_pow feature works with RoutingWrapper.
        """
        # Note that we need correct return value to pass the
        # response filter.
        with patch('pow.ccurl_interface.attach_to_tangle',
                    MagicMock(return_value=self.bundle)) as mocked_ccurl:
            # We are trying to redirect `attach_to_tangle` calls to localhost
            # with a RoutingWrapper. However, if local_pow=true, the pow
            # request will not reach the adapter, but will be directed to
            # ccurl interface. 
            api = Iota(RoutingWrapper('http://12.34.56.78:14265')
                       .add_route('attachToTangle', 'http://localhost:14265'),
                       local_pow=True)
            result = api.attach_to_tangle(
                self.trunk,
                self.branch,
                self.bundle,
                self.mwm)
            self.assertTrue(mocked_ccurl.called)
            self.assertEqual(result['trytes'], self.bundle)
    
    def test_set_local_pow(self):
        """
        Test if local_pow can be enabled/disabled dynamically.
        """
        with patch('pow.ccurl_interface.attach_to_tangle',
                   MagicMock(return_value=self.ccurl_bundle)) as mocked_ccurl:
            self.adapter = MockAdapter()
            self.adapter.seed_response('attachToTangle',{
                'trytes': self.bundle,
            })
            # First, we enable local_pow
            api = Iota(self.adapter, local_pow=True)
            result = api.attach_to_tangle(
                self.trunk,
                self.branch,
                self.bundle,
                self.mwm)
            # Ccurl was called
            self.assertTrue(mocked_ccurl.called)
            # Result comes from ccurl
            self.assertEqual(result['trytes'], self.ccurl_bundle)

            # Reset mock, this clears the called attribute
            mocked_ccurl.reset_mock()

            # Disable local_pow
            api.set_local_pow(local_pow=False)
            # Try again
            result = api.attach_to_tangle(
                self.trunk,
                self.branch,
                self.bundle,
                self.mwm)
            # Ccurl interface was not called
            self.assertFalse(mocked_ccurl.called)
            # Result is the one returned by MockAdapter
            self.assertEqual(result['trytes'], self.bundle)
            # And not by mocked pow pkg
            self.assertNotEqual(result['trytes'], self.ccurl_bundle)