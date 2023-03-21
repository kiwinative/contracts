import ape
from ape.exceptions import ContractLogicError
import pytest

# Standard test comes from the interpretation of EIP-20
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_initial_state(token, owner):
    """
    Test inital state of the contract.
    """
    # Check the token meta matches the deployment
    # token.method_name() has access to all the methods in the smart contract.
    assert token.name() == "KIWINATIVE"
    assert token.symbol() == "KWN"
    assert token.decimals() == 18

    # Check of intial state of authorization
    assert token.owner() == owner
    assert token.isPaused() == False

    # Check intial balance of tokens
    assert token.totalSupply() == 10000000000000 * 10 ** 18
    assert token.balanceOf(owner) == 10000000000000 * 10 ** 18


def test_pause(token, owner, accounts):
    """
    Pauses contract and assert that contract is paused.
    Test that transfers and blacklist is not possible 
    while contract is paused.
    """
    # token.method_name() has access to all the methods in the smart contract.
    token.pause(sender=owner)
    assert token.isPaused() == True
    
    # transaction should not work when contract is paused
    receiver, feeaddress, spender = accounts[1:4]
    with ape.reverts():
        token.transfer(receiver, 100, sender=owner)
        token.approve(spender, 300, sender=owner)
        token.transferFrom(owner, receiver, 300, sender=spender)
    
    assert token.balanceOf(owner) == 10000000000000 * 10 ** 18
    
    
def test_unpause(token, owner, accounts):
    """
    Pauses contract and assert that contract is paused.
    Test that transfers and blacklist is not possible 
    while contract is paused.
    """
    # token.method_name() has access to all the methods in the smart contract.
    token.pause(sender=owner)
    assert token.isPaused() == True
    
    token.unpause(sender=owner)
    assert token.isPaused() == False
    
    # transaction should not work when contract is paused
    receiver, feeaddress, spender = accounts[1:4]
    token.transfer(receiver, 100, sender=owner)
    token.approve(spender, 300, sender=owner)
    token.transferFrom(owner, receiver, 300, sender=spender)
    
    assert token.balanceOf(owner) == 10000000000000 * 10 ** 18 - 400 
        

def test_transfer(token, owner, receiver, feeaddress):
    """
    Transfer must transfer an amount to an address.
    Must trigger Transfer Event.
    Should throw an error of balance if sender does not have enough funds.
    """
    owner_balance = token.balanceOf(owner)
    assert owner_balance == 10000000000000 * 10 ** 18

    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 0

    # token.method_name() has access to all the methods in the smart contract.
    tx = token.transfer(receiver, 100, sender=owner)

    # validate that Transfer Log is correct
    # https://docs.apeworx.io/ape/stable/methoddocs/api.html?highlight=decode#ape.api.networks.EcosystemAPI.decode_logs
    logs = list(tx.decode_logs(token.Transfer))
    assert len(logs) == 3
    assert logs[0].sender == owner
    assert logs[0].receiver == feeaddress
    assert logs[0].amount == int(100 * 0.0001)
    assert logs[1].sender == owner
    assert logs[1].receiver == ZERO_ADDRESS
    assert logs[1].amount == int(100 * 0.0001)
    assert logs[2].sender == owner
    assert logs[2].receiver == receiver
    assert logs[2].amount == 100

    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 100

    owner_balance = token.balanceOf(owner)
    assert owner_balance == 10000000000000 * 10 ** 18 - 100 

    # Expected insufficient funds failure
    # ape.reverts: Reverts the current call using a given snapshot ID.
    # Allows developers to go back to a previous state.
    # https://docs.apeworx.io/ape/stable/methoddocs/api.html?highlight=revert
    with ape.reverts():
        token.transfer(owner, 200, sender=receiver)

    # NOTE: Transfers of 0 values MUST be treated as normal transfers
    # and trigger a Transfer event.
    tx = token.transfer(owner, 0, sender=owner)


def test_transfer_from(token, owner, accounts):
    """
    Transfer tokens to an address.
    Transfer operator may not be an owner.
    Approve must be valid to be a spender.
    """
    receiver, feeaddress, spender = accounts[1:4]

    owner_balance = token.balanceOf(owner)
    assert owner_balance == 10000000000000 * 10 ** 18

    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 0

    # Spender with no approve permission cannot send tokens on someone behalf
    with ape.reverts():
        token.transferFrom(owner, receiver, 300, sender=spender)

    # Get approval for allowance from owner
    tx = token.approve(spender, 300, sender=owner)

    logs = list(tx.decode_logs(token.Approval))
    assert len(logs) == 1
    assert logs[0].owner == owner
    assert logs[0].spender == spender
    assert logs[0].amount == 300

    assert token.allowance(owner, spender) == 300

    # With auth use the allowance to send to receiver via spender(operator)
    tx = token.transferFrom(owner, receiver, 200, sender=spender)

    logs = list(tx.decode_logs(token.Transfer))
    assert len(logs) == 3
    assert logs[0].sender == owner
    assert logs[0].receiver == feeaddress
    assert logs[0].amount == int(200 * 0.0001)
    assert logs[1].sender == owner
    assert logs[1].receiver == '0x0000000000000000000000000000000000000000'
    assert logs[1].amount == int(200 * 0.0001)
    assert logs[2].sender == owner
    assert logs[2].receiver == receiver
    assert logs[2].amount == 200

    assert token.allowance(owner, spender) == 100

    # Cannot exceed authorized allowance
    with ape.reverts():
        token.transferFrom(owner, receiver, 200, sender=spender)

    token.transferFrom(owner, receiver, 100, sender=spender)
    assert token.balanceOf(spender) == 0
    assert token.balanceOf(receiver) == 300
    assert token.balanceOf(owner) == 10000000000000 * 10 ** 18 - 300


def test_approve(token, owner, receiver):
    """
    Check the authorization of an operator(spender).
    Check the logs of Approve.
    """
    spender = receiver

    tx = token.approve(spender, 300, sender=owner)

    logs = list(tx.decode_logs(token.Approval))
    assert len(logs) == 1
    assert logs[0].owner == owner
    assert logs[0].spender == spender
    assert logs[0].amount == 300

    assert token.allowance(owner, spender) == 300

    # Set auth balance to 0 and check attacks vectors
    # though the contract itself shouldn’t enforce it,
    # to allow backwards compatibility
    tx = token.approve(spender, 0, sender=owner)

    logs = list(tx.decode_logs(token.Approval))
    assert len(logs) == 1
    assert logs[0].owner == owner
    assert logs[0].spender == spender
    assert logs[0].amount == 0

    assert token.allowance(owner, spender) == 0


def test_mint(token, owner, receiver):
    """
    Create an approved amount of tokens.
    """
    totalSupply = token.totalSupply()
    assert totalSupply == 10000000000000 * 10 ** 18

    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 0

    tx = token.mint(receiver, 420, sender=owner)

    logs = list(tx.decode_logs(token.Transfer))
    assert len(logs) == 1
    assert logs[0].sender == ZERO_ADDRESS
    assert logs[0].receiver == receiver.address
    assert logs[0].amount == 420

    receiver_balance = token.balanceOf(receiver)
    assert receiver_balance == 420

    totalSupply = token.totalSupply()
    assert totalSupply == 10000000000000 * 10 ** 18 +420


def test_add_minter(token, owner, accounts):
    """
    Test adding new minter.
    Must trigger MinterAdded Event.
    Must return true when checking if target isMinter
    """
    target = accounts[1]
    assert token.isMinter(target) is False
    token.addMinter(target, sender=owner)
    assert token.isMinter(target) is True


def test_add_minter_targeting_zero_address(token, owner):
    """
    Test adding new minter targeting ZERO_ADDRESS
    Must trigger a ContractLogicError (ape.exceptions.ContractLogicError)
    """
    target = ZERO_ADDRESS
    with pytest.raises(ape.exceptions.ContractLogicError) as exc_info:
        token.addMinter(target, sender=owner)
    assert exc_info.value.args[0] == "Cannot add zero address as minter."


def test_burn(token, owner):
    """
    Burn/Send amount of tokens to ZERO Address.
    """
    totalSupply = token.totalSupply()
    assert totalSupply == 10000000000000 * 10 ** 18

    owner_balance = token.balanceOf(owner)
    assert owner_balance == 10000000000000 * 10 ** 18

    tx = token.burn(420, sender=owner)

    # validate that Log is correct
    logs = list(tx.decode_logs(token.Transfer))
    assert len(logs) == 1
    assert logs[0].sender == owner
    assert logs[0].amount == 420

    owner_balance = token.balanceOf(owner)
    assert owner_balance == 10000000000000 * 10 ** 18 -420

    totalSupply = token.totalSupply()
    assert totalSupply == 10000000000000 * 10 ** 18 - 420


def test_permit(chain, token, owner, receiver, Permit):
    """
    Validate permit method for incorrect ownership, values, and timing
    """
    amount = 100
    nonce = token.nonces(owner)
    deadline = chain.pending_timestamp + 60
    assert token.allowance(owner, receiver) == 0
    permit = Permit(owner.address, receiver.address, amount, nonce, deadline)
    signature = owner.sign_message(permit.signable_message).encode_rsv()

    with ape.reverts():
        token.permit(receiver, receiver, amount, deadline, signature, sender=receiver)
    with ape.reverts():
        token.permit(owner, owner, amount, deadline, signature, sender=receiver)
    with ape.reverts():
        token.permit(owner, receiver, amount + 1, deadline, signature, sender=receiver)
    with ape.reverts():
        token.permit(owner, receiver, amount, deadline + 1, signature, sender=receiver)

    token.permit(owner, receiver, amount, deadline, signature, sender=receiver)

    assert token.allowance(owner, receiver) == 100


def test_updateFees(token, owner, feeaddress):
    """
    Updates the txfees as well as the burn fee and address.
    """
    
    # before update
    txfee = token.txfee()
    burnfee = token.burnfee()
    feeAddress = token.feeAddress()
    assert txfee == 1
    assert burnfee == 1
    assert feeAddress == feeaddress

    # update transaction
    tx = token.updateFees(10, 10, feeaddress, sender=owner)
    
    # after update
    txfee = token.txfee()
    burnfee = token.burnfee()
    feeAddress = token.feeAddress()
    assert txfee == 10
    assert burnfee == 10
    assert feeAddress == feeaddress

    # validate that UpdateFees Log is correct
    logs = list(tx.decode_logs(token.UpdateFees))
    assert len(logs) == 1
    assert logs[0].txfee == 10
    assert logs[0].txfee == 10
    assert logs[0].feeAddress == feeAddress
    
    
def test_blacklist(token, owner, accounts):
    """
    Updates the txfees as well as the burn fee and address.
    """
    
    receiver, feeaddress, spender = accounts[1:4]
    
    # initial status of addresses
    assert token.blackListAddresses(receiver) == False
    assert token.blackListAddresses(feeaddress) == False
    assert token.blackListAddresses(spender) == False

    # run transaction
    tx = token.blacklist(spender, True, sender=owner)
    
    # after update
    assert token.blackListAddresses(spender) != False
    token.transfer(spender, 500, sender=owner)
    with ape.reverts():
        token.transfer(receiver, 100, sender=spender)
        token.approve(spender, 300, sender=owner)
        token.transferFrom(owner, receiver, 300, sender=spender)

    # validate that Blacklist Log is correct
    logs = list(tx.decode_logs(token.Blacklist))
    assert len(logs) == 1
    assert logs[0].blackListed == spender
    assert logs[0].value == True
    
    
def test_transferOwnership(token, owner, accounts):
    """
    Updates the txfees as well as the burn fee and address.
    """
    
    newOwner = accounts[4]
    
    # initial status of addresses
    assert token.owner() == owner

    # run transaction
    tx = token.transferOwnership(newOwner, sender=owner)
    
    # after update
    assert token.owner() == newOwner

    # validate that OwnershipTransferred Log is correct
    logs = list(tx.decode_logs(token.OwnershipTransferred))
    assert len(logs) == 1
    assert logs[0].previousOwner == owner
    assert logs[0].newOwner == newOwner