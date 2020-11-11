from iota.multisig.commands import GetDigestsCommand


def get_digest(seed, index, security):

  GetDigestsCommand(self.adapter)(
    seed=self.seed,
    index=index,
    count=count,
    securityLevel=security_level,
  )

  return {
    'digest': IOTACrypto.multisig.getDigest(seed, index, security),
    'security': security,
    'index': index
  }
