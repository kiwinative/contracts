import pytest
from ape import Contract
from eip712.messages import EIP712Message


@pytest.fixture(scope="session")
def Permit(chain, token):
    class Permit(EIP712Message):
        _name_: "string" = "KIWI"
        _version_: "string" = "1.0"
        _chainId_: "uint256" = chain.chain_id
        _verifyingContract_: "address" = token.address

        owner: "address"
        spender: "address"
        value: "uint256"
        nonce: "uint256"
        deadline: "uint256"

    return Permit


@pytest.fixture(scope="session")
def owner(accounts):
    return accounts[0]

@pytest.fixture(scope="session")
def receiver(accounts):
    return accounts[1]

@pytest.fixture(scope="session")
def feeaddress(accounts):
    return accounts[2]

@pytest.fixture(scope="session")
def wallet(accounts):
    return accounts[5]

@pytest.fixture(scope="session")
def token(owner, project, feeaddress):
    return owner.deploy(project.Token, 1, 1, feeaddress)

@pytest.fixture(scope="session")
def crowdSale(owner, project, wallet, token):
    return owner.deploy(project.Crowdsale, token.address, wallet, 1)

@pytest.fixture(scope="session")
def roulette(wallet, project, token):
    return wallet.deploy(project.Roulette, token.address)

@pytest.fixture(scope="session")
def sport(wallet, project, token):
    return wallet.deploy(project.Sport, token.address)