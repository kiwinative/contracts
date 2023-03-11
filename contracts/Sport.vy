import Token as Token


struct Bet:
    player1: address
    player2: address
    amount: uint256
    player1Won: bool
    betTime: uint256
    resolveTime: uint256

# State Variables
kiwiToken: public(Token)
bets: public(HashMap[uint256, Bet])
betCount: public(uint256)

# Events
event BetPlaced:
    betId: uint256
    player1: indexed(address)
    player2: indexed(address)
    amount: uint256
    betTime: uint256

event BetResolved:
    betId: uint256
    player1: indexed(address)
    player2: indexed(address)
    amount: uint256
    player1Won: bool
    resolveTime: uint256



@external
def __init__(_kiwiTokenAddress: address):
    """
    @notice Constructor, runs at contracts deployment.
    @param _kiwiTokenAddress KIWI token address
    """

    assert _kiwiTokenAddress != empty(address)
    self.kiwiToken = Token(_kiwiTokenAddress)


@external
def placeBet(player2: address, amount: uint256):
        assert player2 != empty(address), "Invalid player 2 address."
        self.bets[self.betCount] = Bet({
            player1: msg.sender,
            player2: player2,
            amount: amount,
            player1Won: False,
            betTime: block.timestamp,
            resolveTime: 0
        })
        self.betCount += 1
        log BetPlaced(self.betCount-1, msg.sender, player2, amount, block.timestamp)

@external
def transfer(_from: address, _to: address, _amount: uint256):
    self.kiwiToken.transferFrom(_from, _to, _amount,)