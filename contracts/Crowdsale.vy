# @version 0.3.7

import Token as Token

# Crowdsale stae variables

kiwiToken: public(Token)    # $KIWI
wallet: public(address)     # Address where the funds are collected
rate: public(uint256)       # How many token units a buyer gets per GWei (10-9 or 0.000000001 BNB)
gweiRaised: public(uint256)

# Events
event TokenPurchase:
    purchaser: indexed(address)
    beneficiary: indexed(address)
    value: uint256
    amount: uint256

owner: public(address)


@external
def __init__(_kiwiTokenAddress: address, _wallet: address, _rate: uint256):
    """
    @notice Constructor, runs at contracts deployment.
    @param _kiwiTokenAddress KIWI token address
    @param _wallet The address where collected funds will be forwarded to
    @param _rate The number of KIWI a buyer gets per gwei
    """

    assert _rate > 0
    assert _wallet != empty(address)
    assert _kiwiTokenAddress != empty(address)

    self.owner = msg.sender
    self.kiwiToken = Token(_kiwiTokenAddress)
    self.wallet = _wallet
    self.rate = _rate


@view
@internal
def _getTokenAmount(_gweiAmount: uint256) -> uint256:
    """
    @notice Function to converts BNB(Gwei) to tokens
    @param _gweiAmount amount of gwei to be converted
    @return Number of kiwi tokens that can be purchase wit the speciified amount of _gweiAmount.
    """

    return _gweiAmount * self.rate


@internal
def _buyTokens(_beneficiary: address, _gweiAmount: uint256) -> bool:
    """
    @notice Internal function to buy KIWI token
    @param _beneficiary address to foward token to.
    @return True, on transaction successfull.
    """

    assert _beneficiary != empty(address)
    assert _gweiAmount > 0

    kiwi: uint256 = self._getTokenAmount(_gweiAmount)

    self.gweiRaised += _gweiAmount

    assert self.kiwiToken.transferFrom(self.kiwiToken.owner(), _beneficiary, kiwi)

    log TokenPurchase(msg.sender, _beneficiary, _gweiAmount, kiwi)

    send(self.wallet, _gweiAmount)
    return True


@external
@payable
def buyTokens(_beneficiary: address) -> bool:
    """
    @notice Function to buy KIWI token
    @param _beneficiary address to foward token to.
    @return True, on transaction successfull.
    """
    self._buyTokens(_beneficiary, msg.value)
    return True

@external
@payable
def __default__():
    """
    @dev fallback function ***DO NOT OVERRIDE***
    """
    # print(self.owner)
    self._buyTokens(msg.sender, msg.value)