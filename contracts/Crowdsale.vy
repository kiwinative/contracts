# @version 0.3.7

import Token as Token

# Crowdsale stae variables

kiwinativeToken: public(Token)    # $KIWINATIVE
wallet: public(address)     # Address where the funds are collected
rate: public(uint256)       # How many token units a buyer gets per Wei (10-18 or 0.000000000000000001 BNB)
weiRaised: public(uint256)

# Events
event TokenPurchase:
    purchaser: indexed(address)
    beneficiary: indexed(address)
    value: uint256
    amount: uint256

event UpdateRate:
    rate: uint256

owner: public(address)


@external
def __init__(_kiwinativeTokenAddress: address, _wallet: address, _rate: uint256):
    """
    @notice Constructor, runs at contracts deployment.
    @param _kiwinativeTokenAddress KWN token address
    @param _wallet The address where collected funds will be forwarded to
    @param _rate The number of KWN a buyer gets per wei
    """

    assert _rate > 0
    assert _wallet != empty(address)
    assert _kiwinativeTokenAddress != empty(address)

    self.owner = msg.sender
    self.kiwinativeToken = Token(_kiwinativeTokenAddress)
    self.wallet = _wallet
    self.rate = _rate


@external
def updateRate(_rate: uint256) -> bool:
    """
    @notice Function to update rate
    @param _rate The new rate per wei.
    @return A boolean that indicates if the operation was successful.
    """

    assert msg.sender == self.owner, "Access is denied."
    self.rate = _rate

    log UpdateRate(_rate)

    return True


@view
@internal
def _getTokenAmount(_weiAmount: uint256) -> uint256:
    """
    @notice Function to converts BNB(wei) to tokens
    @param _weiAmount amount of wei to be converted
    @return Number of kiwinative tokens that can be purchase wit the speciified amount of _weiAmount.
    """

    return _weiAmount * self.rate


@internal
def _buyTokens(_beneficiary: address, _weiAmount: uint256) -> bool:
    """
    @notice Internal function to buy KIWINATIVE token
    @param _beneficiary address to foward token to.
    @return True, on transaction successfull.
    """

    assert _beneficiary != empty(address)
    assert _weiAmount > 0

    kiwinative: uint256 = self._getTokenAmount(_weiAmount)

    self.weiRaised += _weiAmount

    assert self.kiwinativeToken.transferFrom(self.kiwinativeToken.owner(), _beneficiary, kiwinative)

    log TokenPurchase(msg.sender, _beneficiary, _weiAmount, kiwinative)

    send(self.wallet, _weiAmount)
    return True


@external
@payable
def buyTokens(_beneficiary: address) -> bool:
    """
    @notice Function to buy KIWINATIVE token
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


@external
def destroy() -> bool:
    """
    @notice Function to destroy contract
    @return A boolean that indicates if the operation was successful.
    """

    assert msg.sender == self.owner, "Access is denied."
    selfdestruct(msg.sender)