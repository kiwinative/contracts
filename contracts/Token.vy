# @version 0.3.7

from vyper.interfaces import ERC20


implements: ERC20

# ERC20 Token Metadata
NAME: constant(String[20]) = "KIWI"
SYMBOL: constant(String[5]) = "KWI"
DECIMALS: constant(uint8) = 18

# ERC20 State Variables
totalSupply: public(uint256)
balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])

# KIWI token state variable
isPaused: public(bool)
blackListAddresses: public(HashMap[address, bool])
txfee: public(uint256)
burnfee: public(uint256)
feeAddress: public(address)

# Events
event Paused: pass

event Unpaused: pass

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    amount: uint256

event OwnershipTransferred:
    previousOwner: indexed(address)
    newOwner: indexed(address)

event Blacklist:
    blackListed: indexed(address)
    value: bool

event UpdateFees:
    txfee: uint256
    burnfee: uint256
    feeAddress: indexed(address)

owner: public(address)
isMinter: public(HashMap[address, bool])

nonces: public(HashMap[address, uint256])
DOMAIN_SEPARATOR: public(bytes32)
DOMAIN_TYPE_HASH: constant(bytes32) = keccak256('EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)')
PERMIT_TYPE_HASH: constant(bytes32) = keccak256('Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)')


@external
def __init__(_txfee: uint256, _burnfee: uint256, _feeAddress: address):
    """
    @notice Constructor, runs at contracts deployment.
    @param _txfee The txfee
    @param _burnfee The burnfee
    @param _feeAddress The address to transfer txfee to.
    """

    self.owner = msg.sender
    self.totalSupply = 100000000000000000000
    self.balanceOf[msg.sender] = 100000000000000000000
    self.txfee = _txfee
    self.burnfee = _burnfee
    self.feeAddress = _feeAddress

    # EIP-712
    self.DOMAIN_SEPARATOR = keccak256(
        concat(
            DOMAIN_TYPE_HASH,
            keccak256(NAME),
            keccak256("1.0"),
            _abi_encode(chain.id, self)
        )
    )

    log Transfer(empty(address), msg.sender, 100000000000000000000)


@pure
@external
def name() -> String[20]:
    """
    @notice Gets the tokens name.
    @return String[20], if transaction completes successfully
    """
    
    return NAME


@pure
@external
def symbol() -> String[5]:
    """
    @notice Gets the tokens symbol.
    @return String[5], if transaction completes successfully
    """

    return SYMBOL


@pure
@external
def decimals() -> uint8:
    """
    @notice Gets the tokens decimals.
    @return uint8, if transaction completes successfully
    """

    return DECIMALS


@external
def pause() -> bool:
    """
    @notice Function to pause contract.
    @return A boolean that indicates if the operation was successful.
    """
    
    assert msg.sender == self.owner, "Access is denied."
    assert self.isPaused == False

    self.isPaused = True

    log Paused()

    return True


@external
def unpause() -> bool:
    """
    @notice Function to pause contract.
    @return A boolean that indicates if the operation was successful.
    """
    
    assert msg.sender == self.owner, "Access is denied."
    assert self.isPaused == True

    self.isPaused = False

    log Unpaused()

    return True


@internal
def _blackList(_address: address, _isblackListed: bool) -> bool:
    """
    @notice 
        Internal function to blacklist an adress.
        used in the external function blackList().
    @param _address The address to be either blacklisted or whitelisted.
    @param _isblacklisted The address' blacklist state.
    @return True, if transaction completes successfully.
    """

    assert self.blackListAddresses[_address] != _isblackListed

    self.blackListAddresses[_address] = _isblackListed

    log Blacklist(_address, _isblackListed)
    return True


@internal
def _decay(_address: address, _value: uint256) -> uint256:
    """
    @notice 
        Internal function that implements deflationary decay on transaction.
    @param _address The address of the sender.
    @param _value The address' value to be sent.
    @return uint256, if transaction completes successfully.
    """

    tempValue: uint256 = _value
    newValue: uint256 = _value
    if self.txfee > 0 and _address != self.feeAddress:
        deflationaryDecay: uint256 = tempValue / (10000 / self.txfee)
        self.balanceOf[self.feeAddress] += deflationaryDecay
        log Transfer(_address, self.feeAddress, deflationaryDecay)
        newValue -= deflationaryDecay

    if self.burnfee > 0 and _address != self.feeAddress:
        burnValue: uint256 = tempValue / (10000 / self.burnfee)
        self.totalSupply -= self.totalSupply
        log Transfer(_address, empty(address), burnValue)
        newValue -= burnValue
    return newValue


@external
def transfer(receiver: address, amount: uint256) -> bool:
    """
    @notice Transfers token to receipient.
    @param receiver The address of the receipient.
    @param amount The amount to be transfered.
    @return True, if transaction completes successfully
    """

    assert self.isPaused == False
    assert self.blackListAddresses[msg.sender] == False
    assert receiver not in [empty(address), self]

    self.balanceOf[msg.sender] -= amount
    newAmount: uint256 = self._decay(msg.sender, amount)
    self.balanceOf[receiver] += newAmount

    log Transfer(msg.sender, receiver, newAmount)
    return True


@external
def transferFrom(sender:address, receiver: address, amount: uint256) -> bool:
    """
    @notice Transfers token to receipient on behalf of a sender.
    @param sender The address of the sender.
    @param receiver The address of the receipient.
    @param amount The amount to be transfered.
    @return True, if transaction completes successfully
    """

    assert self.isPaused == False
    assert self.blackListAddresses[msg.sender] == False
    assert receiver not in [empty(address), self]

    newAmount: uint256 = self._decay(sender, amount)

    self.allowance[sender][msg.sender] -= newAmount
    self.balanceOf[sender] -= amount
    self.balanceOf[receiver] += newAmount

    log Transfer(sender, receiver, newAmount)
    return True


@external
def approve(spender: address, amount: uint256) -> bool:
    """
    @param spender The address that will execute on owner behalf.
    @param amount The amount of token to be transfered.
    """

    assert self.isPaused == False
    self.allowance[msg.sender][spender] = amount

    log Approval(msg.sender, spender, amount)
    return True


@external
def burn(amount: uint256) -> bool:
    """
    @notice Burns the supplied amount of tokens from the sender wallet.
    @param amount The amount of token to be burned.
    """

    assert self.isPaused == False
    self.balanceOf[msg.sender] -= amount
    self.totalSupply -= amount

    log Transfer(msg.sender, empty(address), amount)

    return True


@external
def mint(receiver: address, amount: uint256) -> bool:
    """
    @notice Function to mint tokens
    @param receiver The address that will receive the minted tokens.
    @param amount The amount of tokens to mint.
    @return A boolean that indicates if the operation was successful.
    """
    
    assert msg.sender == self.owner or self.isMinter[msg.sender], "Access is denied."
    assert receiver not in [empty(address), self]

    self.totalSupply += amount
    self.balanceOf[receiver] += amount

    log Transfer(empty(address), receiver, amount)

    return True


@external
def addMinter(target: address) -> bool:
    """
    @notice Function to give add a minter
    @param target The address of the minter to be added
    @return A boolean that indicates if the operation was successful.
    """

    assert msg.sender == self.owner
    assert target != empty(address), "Cannot add zero address as minter."
    self.isMinter[target] = True
    return True


@external
def permit(owner: address, spender: address, amount: uint256, expiry: uint256, signature: Bytes[65]) -> bool:
    """
    @notice
        Approves spender by owner's signature to expend owner's tokens.
        See https://eips.ethereum.org/EIPS/eip-2612.
    @param owner The address which is a source of funds and has signed the Permit.
    @param spender The address which is allowed to spend the funds.
    @param amount The amount of tokens to be spent.
    @param expiry The timestamp after which the Permit is no longer valid.
    @param signature A valid secp256k1 signature of Permit by owner encoded as r, s, v.
    @return True, if transaction completes successfully
    """
    assert owner != empty(address)  # dev: invalid owner
    assert expiry == 0 or expiry >= block.timestamp  # dev: permit expired
    nonce: uint256 = self.nonces[owner]
    digest: bytes32 = keccak256(
        concat(
            b'\x19\x01',
            self.DOMAIN_SEPARATOR,
            keccak256(
                _abi_encode(
                    PERMIT_TYPE_HASH,
                    owner,
                    spender,
                    amount,
                    nonce,
                    expiry,
                )
            )
        )
    )
    # NOTE: signature is packed as r, s, v
    r: uint256 = convert(slice(signature, 0, 32), uint256)
    s: uint256 = convert(slice(signature, 32, 32), uint256)
    v: uint256 = convert(slice(signature, 64, 1), uint256)
    assert ecrecover(digest, v, r, s) == owner  # dev: invalid signature
    self.allowance[owner][spender] = amount
    self.nonces[owner] = nonce + 1

    log Approval(owner, spender, amount)
    return True


@external
def updateFees(newTxfee: uint256, newBurnfee: uint256, newFeeAddress: address) -> bool:
    """
    @notice Updates the txfees as well as the burn fee and address
    @param  newTxfee The new txfee.
    @param  newBurnfee The new burnfee.
    @param  newFeeAddress The new tx address.
    @return True, if transaction completes successfully
    """
    assert msg.sender == self.owner
    assert newFeeAddress != empty(address), "Cannot add zero address as new fee address."
    self.txfee = newTxfee
    self.burnfee = newBurnfee
    self.feeAddress = newFeeAddress
    log UpdateFees(newTxfee, newBurnfee, newFeeAddress)
    return True


@external
def blacklist(listAddress: address, isblackListed: bool) -> bool:
    """
    @notice External function to blacklist an adress.
    @param listAddress The address to be either blacklisted or whitelisted.
    @param isblackListed The address' blacklist state.
    @return True, if transaction completes successfully.
    """

    assert self.isPaused == False
    return self._blackList(listAddress, isblackListed)


@external
def transferOwnership(newOwner: address) -> bool:
    """
    @notice Transfers token ownership
    @param  newOwner The address to transfer token ownership to.
    @return True, if transaction completes successfully
    """
    assert msg.sender == self.owner
    assert newOwner != empty(address), "Cannot add zero address as new owner."
    log OwnershipTransferred(self.owner, newOwner)
    self.owner = newOwner
    return True