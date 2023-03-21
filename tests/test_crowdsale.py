import ape
import pytest
from ape.exceptions import ContractError

# Standard test comes from the interpretation of EIP-20
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_initial_state(token, crowdSale, owner, wallet):
    """
    Test inital state of the contract.
    """
    # Check the token meta matches the deployment
    # token.method_name() has access to all the methods in the smart contract.
    assert crowdSale.kiwinativeToken() == token
    assert crowdSale.wallet() == wallet
    assert crowdSale.rate() == 1
    assert crowdSale.weiRaised() == 0

    # Check of intial state of authorization
    assert crowdSale.owner() == owner
    

def test_default_state(chain, token, crowdSale, owner, accounts, wallet, Permit):
    """
    Test default state of contract.
    sender must be forwarded KIWI once he send Gwei to crowd sale contract.
    """
    
    wallet_balance = 1000000 * 10 ** 18
    signer = accounts[6]
    signer_balance = signer.balance
    assert signer_balance == wallet_balance
    assert wallet.balance == wallet_balance
    
    assert token.balanceOf(owner) == 10000000000000 * 10 ** 18

    token.approve(crowdSale.address, 100000, sender=owner)
    
    assert token.allowance(owner, crowdSale.address) == 100000
    tx = signer.transfer(crowdSale, 100)
    
    assert signer.balance < signer_balance
    assert crowdSale.weiRaised() == 100
    assert wallet.balance == wallet_balance + 100
    assert token.allowance(owner, signer) == 0
    assert token.balanceOf(signer) == 100
    
    logs = list(tx.decode_logs(crowdSale.TokenPurchase))
    assert len(logs) == 1
    assert logs[0].purchaser == signer
    assert logs[0].beneficiary == signer
    assert logs[0].value == 100
    assert logs[0].amount == 100
    
    
    
def test_buyTokens(token, crowdSale, owner, accounts, wallet, chain, Permit):
    """
    Test bytToken function.
    buyToken forward KIWI to the purchaser once it recieves gwei.
    """
    
    wallet_balance = 1000000000000000000000000
    signer = accounts[6]
    signer_balance = signer.balance
    assert signer_balance == wallet_balance
    assert wallet.balance == wallet_balance

    token.approve(crowdSale.address, 100000, sender=owner)
    
    assert token.allowance(owner, crowdSale.address) == 100000
    
    tx = crowdSale.buyTokens(signer, sender=signer, value=100)
    
    assert signer.balance < signer_balance
    assert crowdSale.weiRaised() == 100
    assert wallet.balance == wallet_balance + 100
    assert token.allowance(owner, owner) == 0
    assert token.balanceOf(signer) == 100
    
    logs = list(tx.decode_logs(crowdSale.TokenPurchase))
    assert len(logs) == 1
    assert logs[0].purchaser == signer
    assert logs[0].beneficiary == signer
    assert logs[0].value == 100
    assert logs[0].amount == 100


def test_update_rate(crowdSale, owner, wallet):
    """
    Test update rate function.
    """
    rate = 200
    
    assert crowdSale.rate() == 1
    
    with ape.reverts():
        crowdSale.updateRate(rate, sender=wallet)
    
    crowdSale.updateRate(rate, sender=owner)
    
    assert crowdSale.rate() == rate
    
    
def test_destroy(token, crowdSale, owner, wallet):
    """
    Test destroy function.
    """
    # Check the token meta matches the deployment
    # token.method_name() has access to all the methods in the smart contract.
    assert crowdSale.kiwinativeToken() == token
    assert crowdSale.wallet() == wallet
    assert crowdSale.rate() == 1
    assert crowdSale.weiRaised() == 0
    
    assert crowdSale.owner() == owner
    
    with ape.reverts():
        crowdSale.destroy(sender=wallet)
    
    crowdSale.destroy(sender=owner)