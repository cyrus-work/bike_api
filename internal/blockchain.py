from web3 import Web3

from internal.app_config import token_abi, network_config_parse, testnet, setting, mainnet
from internal.log import logger

if setting["testMode"]:
    logger.info(">>> network config parse testnet")
    polygon_rpc_url, private_key, token_address, chain_id = network_config_parse(testnet)
else:
    logger.info(">>> network config parse mainnet")
    polygon_rpc_url, private_key, token_address, chain_id = network_config_parse(mainnet)
web3 = Web3(Web3.HTTPProvider(polygon_rpc_url))


def get_check_sum_address(address: str):
    """
    주소를 체크섬 주소로 변환하는 함수

    :param address: 주소
    :return: 체크섬 주소 데이터의 json
    """
    address = address.lower()
    address = web3.to_checksum_address(address)
    return address


def act_transfer(from_address: str, to_address: str, amount: int, private_key_str: str, nonce: int):
    """
    토큰을 전송하는 함수

    :param from_address: 보내는 주소
    :param to_address: 받는 주소
    :param amount: 전송 금액
    :param private_key_str: 보내는 주소의 개인키
    :param nonce: nonce
    :return: 전송 결과
    """
    logger.info(f"from_address: {from_address}")
    logger.info(f"nonce: {nonce}")
    token_contract = web3.eth.contract(address=token_address, abi=token_abi)
    tx = token_contract.functions.transfer(to_address, amount).build_transaction(
        {"chainId": chain_id, "gas": 200_000, "gasPrice": web3.to_wei("10", "gwei"), "nonce": nonce}
    )
    logger.info(f"tx: {tx}")
    signed_tx = web3.eth.account.sign_transaction(tx, private_key_str)
    logger.info(f"signed_tx: {signed_tx}")
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    logger.info(f"tx_hash: {tx_hash}")
    return tx_hash.hex()


def lock_transfer(from_address: str, to_address: str, amount: int, private_key_str: str, nonce: int, lock_time: int):
    """
    토큰을 전송하는 함수

    :param from_address: 보내는 주소
    :param to_address: 받는 주소
    :param amount: 전송 금액
    :param private_key_str: 보내는 주소의 개인키
    :param nonce: nonce
    :param lock_time: 잠금 시간
    :return: 전송 결과
    """
    logger.info(f"from_address: {from_address}")
    logger.info(f"nonce: {nonce}")
    token_contract = web3.eth.contract(address=token_address, abi=token_abi)
    tx = token_contract.functions.transferWithLock(to_address, amount, lock_time).build_transaction(
        {"chainId": chain_id, "gas": 200_000, "gasPrice": web3.to_wei("10", "gwei"), "nonce": nonce}
    )
    signed_tx = web3.eth.account.sign_transaction(tx, private_key_str)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()


def reward_transfer(to_address: str, amount: int, nonce: int):
    """
    보상을 전송하는 함수

    :param to_address: 받는 주소
    :param amount: 전송 금액
    :param private_key_str: 보내는 주소의 개인키
    :param nonce: nonce
    :return: 전송 결과
    """
    private_key_str = private_key
    from_address = web3.eth.account.from_key(private_key_str).address
    return act_transfer(from_address, to_address, amount, private_key_str, nonce)


def level_reward_transfer(to_address: str, amount: int, nonce: int, lock_time: int):
    """
    레벨 보상을 전송하는 함수

    :param to_address: 받는 주소
    :param amount: 전송 금액
    :param private_key_str: 보내는 주소의 개인키
    :param nonce: nonce
    :param lock_time: 잠금 시간
    :return: 전송 결과
    """
    private_key_str = private_key
    from_address = web3.eth.account.from_key(private_key_str).address
    return lock_transfer(from_address, to_address, amount, private_key_str, nonce, lock_time)
