import ape
import pytest
from ethpm_types.utils import HexBytes

# Standard test comes from the interpretation of EIP-20
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_initial_state(token, sport, wallet, accounts, owner):
    """
    Test inital state of the contract.
    """
    # Check the meta matches the deployment
    assert sport.kiwiToken() == token
    
    to = accounts[9]
    assert token.balanceOf(to) == 0
    token.transfer(wallet, 10000, sender=owner)
    token.approve(sport.address, 1000, sender=wallet)
    sport.transfer(wallet, to, 1000, sender=to)
    
    assert token.balanceOf(to) == 1000