import Token as Token

struct BettingEvent:
    

# State Variables
kiwiToken: public(Token)
bets: public(HashMap[uint256, Bet])
betCount: public(uint256)

# Events




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