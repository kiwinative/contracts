from web3 import Web3, HTTPProvider
          
def test_block_number():
    url = 'https://data-seed-prebsc-1-s1.binance.org:8545/' 
    
    web3 = Web3(HTTPProvider(url))
    print(web3.eth.block_number, web3.is_connected())
    print(web3.eth.get_transaction_count('0x293F2c29d2Bc578BF112d59e103a386ad8817f87'))
    
    contract_bytecode = '0x60206104516000396000518060a01c61044c5760405260206104716000396000518060a01c61044c576060523461044c5760206104916000396000511561044c576060511561044c576040511561044c573360045560405160005560605160015560206104916000396000516002556103cb610080610000396103cb610000f36003361161000c57610250565b60003560e01c63ec8ac4d8811861005b57602436106103b9576004358060a01c6103b9576101c0526101c0516060523460805261004a6101e0610288565b6101e05060016101e05260206101e0f35b6369ea1771811861011757602436106103b957346103b9576004543318156100da5760116040527f4163636573732069732064656e6965642e00000000000000000000000000000060605260405060405180606001601f826000031636823750506308c379a06000526020602052601f19601f6040510116604401601cfd5b6004356002557fc04ab144c3f6fd32b71825eb92c20af3c8b2f2b6680dfaf3645b527f098c245b60043560405260206040a1600160405260206040f35b6383197ef0811861019a57600436106103b957346103b9576004543318156101965760116040527f4163636573732069732064656e6965642e00000000000000000000000000000060605260405060405180606001601f826000031636823750506308c379a06000526020602052601f19601f6040510116604401601cfd5b33fff35b6390069e9881186101be57600436106103b957346103b95760005460405260206040f35b63521eb27381186101e257600436106103b957346103b95760015460405260206040f35b632c4e722e811861020657600436106103b957346103b95760025460405260206040f35b634042b66f811861022a57600436106103b957346103b95760035460405260206040f35b638da5cb5b811861024e57600436106103b957346103b95760045460405260206040f35b505b33606052346080526102636101c0610288565b6101c050005b6040516002548082028115838383041417156103b95790509050815250565b606051156103b957608051156103b9576080516040526102a860c0610269565b60c05160a0526003546080518082018281106103b957905090506003556000546323b872dd61012052600054638da5cb5b60c052602060c0600460dc845afa6102f6573d600060003e3d6000fd5b60203d106103b95760c0518060a01c6103b95761010052610100905051610140526060516101605260a051610180526020610120606461013c6000855af1610343573d600060003e3d6000fd5b60203d106103b957610120518060011c6103b9576101a0526101a0905051156103b957606051337f623b3804fa71d67900d064613da8f94b9617215ee90799290593e1745087ad1860805160c05260a05160e052604060c0a360006000600060006080516001546000f1156103b9576001815250565b600080fda165767970657283000307000b005b600080fd' # replace with your contract bytecode
    
    contract_abi = '[{"anonymous":false,"inputs":[{"indexed":true,"name":"purchaser","type":"address"},{"indexed":true,"name":"beneficiary","type":"address"},{"indexed":false,"name":"value","type":"uint256"},{"indexed":false,"name":"amount","type":"uint256"}],"name":"TokenPurchase","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"rate","type":"uint256"}],"name":"UpdateRate","type":"event"},{"inputs":[{"name":"_kiwinativeTokenAddress","type":"address"},{"name":"_wallet","type":"address"},{"name":"_rate","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"name":"_rate","type":"uint256"}],"name":"updateRate","outputs":[{"name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"_beneficiary","type":"address"}],"name":"buyTokens","outputs":[{"name":"","type":"bool"}],"stateMutability":"payable","type":"function"},{"stateMutability":"payable","type":"fallback"},{"inputs":[],"name":"destroy","outputs":[{"name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"kiwinativeToken","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"wallet","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"rate","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"weiRaised","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"}]'
    # Create a deployment transaction
    contract = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    transaction = contract.constructor('0xac1b538AbF3d9EB735cCB933b4a327Eef0688EF5', '0x11D66E6AE8f07E343838059BDc5819A6A9B17037', 1).build_transaction({
        'from': '0x293F2c29d2Bc578BF112d59e103a386ad8817f87', # replace with your testnet BNB address
        'nonce': web3.eth.get_transaction_count('0x293F2c29d2Bc578BF112d59e103a386ad8817f87'), # replace with your testnet BNB address
        'gas': 1219695,
        'gasPrice': web3.to_wei('10', 'gwei')
    })

    # Sign and send the deployment transaction
    signed = web3.eth.account.signTransaction(transaction, '123c574b6cbf96e91b372d6059da6f7049004d504822229dfd5927f1678aa44b') # replace with the private key of your testnet BNB address
    transaction_hash = web3.eth.send_raw_transaction(signed.rawTransaction)

    # Wait for the deployment to be mined
    transaction_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)

    # The contract address is the address of the last returned log
    contract_address = transaction_receipt['contractAddress']
    print(contract_address)

    # Now you can interact with the deployed contract using the contract address and ABI
    # contract_instance = web3.eth.contract(address='0x7a1C309D91740f20Bdd1b2695f457B7B1e31D06c', abi=contract_abi)
    # transaction = contract_instance.functions.mint('0x21c683Ee36243d01dFDB2fbA4f8c1A8FC8C4cD49', 10000000 *10 ** 18,).build_transaction({
    #     'from': '0x21c683Ee36243d01dFDB2fbA4f8c1A8FC8C4cD49', # replace with your testnet BNB address
    #     'nonce': web3.eth.get_transaction_count('0x21c683Ee36243d01dFDB2fbA4f8c1A8FC8C4cD49'), # replace with your testnet BNB address
    #     'gas': 1219695,
    #     'gasPrice': web3.to_wei('5', 'gwei')
    # })
    
    # signed = web3.eth.account.signTransaction(transaction, 'e88b1d0208d41bfc852b597e85e4320389dd338361a53c90ca60ab99ca6e5387') # replace with the private key of your testnet BNB address
    # transaction_hash = web3.eth.send_raw_transaction(signed.rawTransaction)
    
if __name__ == "__main__":
    test_block_number()