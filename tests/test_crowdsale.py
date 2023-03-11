import ape
import pytest

# Standard test comes from the interpretation of EIP-20
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_initial_state(token, crowdSale, owner, wallet):
    """
    Test inital state of the contract.
    """
    # Check the token meta matches the deployment
    # token.method_name() has access to all the methods in the smart contract.
    assert crowdSale.kiwiToken() == token
    assert crowdSale.wallet() == wallet
    assert crowdSale.rate() == 1
    assert crowdSale.gweiRaised() == 0

    # Check of intial state of authorization
    assert crowdSale.owner() == owner
    

def test_default_state(chain, token, crowdSale, owner, accounts, wallet, Permit):
    """
    Test default state of contract.
    sender must be forwarded KIWI once he send Gwei to crowd sale contract.
    """
    
    wallet_balance = 1000000000000000000000000
    signer = accounts[6]
    signer_balance = signer.balance
    assert signer_balance == wallet_balance
    assert wallet.balance == wallet_balance
    
    assert token.balanceOf(owner) == 100000000000000000000
    
    nonce = token.nonces(owner)
    deadline = chain.pending_timestamp + 60
    permit = Permit(owner.address, crowdSale.address, 100000, nonce, deadline)
    signature = owner.sign_message(permit.signable_message).encode_rsv()

    token.permit(owner, crowdSale.address, 100000, deadline, signature, sender=signer)
    
    assert token.allowance(owner, crowdSale.address) == 100000
    tx = signer.transfer(crowdSale, 100)
    
    assert signer.balance < signer_balance
    assert crowdSale.gweiRaised() == 100
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
    
    nonce = token.nonces(owner)
    deadline = chain.pending_timestamp + 60
    permit = Permit(owner.address, crowdSale.address, 100000, nonce, deadline)
    signature = owner.sign_message(permit.signable_message).encode_rsv()

    token.permit(owner, crowdSale.address, 100000, deadline, signature, sender=signer)
    
    assert token.allowance(owner, crowdSale.address) == 100000
    
    tx = crowdSale.buyTokens(signer, sender=signer, value=100)
    
    assert signer.balance < signer_balance
    assert crowdSale.gweiRaised() == 100
    assert wallet.balance == wallet_balance + 100
    assert token.allowance(owner, owner) == 0
    assert token.balanceOf(signer) == 100
    
    logs = list(tx.decode_logs(crowdSale.TokenPurchase))
    assert len(logs) == 1
    assert logs[0].purchaser == signer
    assert logs[0].beneficiary == signer
    assert logs[0].value == 100
    assert logs[0].amount == 100
