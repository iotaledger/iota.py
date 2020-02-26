from iota import AsyncIota, ProposedTransaction, Address, TryteString
from typing import List
import asyncio

# Asynchronous API instance.
api = AsyncIota(
        adapter='https://nodes.devnet.iota.org:443',
        devnet=True,
)

# An arbitrary address to send zero-value transactions to.
addy = Address('PZITJTHCIIANKQWEBWXUPHWPWVNBKW9GMNALMGGSIAUOYCKNWDLUUIGAVMJYCHZXHUBRIVPLFZHUVDLME')

# Timeout after which confirmation monitoring stops (seconds).
timeout = 120
# How often should we poll for confirmation? (seconds)
polling_interval = 5


async def send_and_monitor(
    transactions: List[ProposedTransaction]
) -> bool:
    """
    Send a list of transactions as a bundle and monitor their confirmation
    by the network.
    """
    print('Sending bundle...')
    st_response = await api.send_transfer(transactions)

    sent_tx_hashes = [tx.hash for tx in st_response['bundle']]

    print('Sent bundle with transactions: ')
    print(*sent_tx_hashes, sep='\n')

    # Measure elapsed time
    elapsed = 0

    print('Checking confirmation...')
    while len(sent_tx_hashes) > 0:
        # Determine if transactions are confirmed
        gis_response = await api.get_inclusion_states(sent_tx_hashes, None)

        for i, (tx, is_confirmed) in enumerate(zip(sent_tx_hashes, gis_response['states'])):
            if is_confirmed:
                print('Transaction %s is confirmed.' % tx)
                # No need to check for this any more
                del sent_tx_hashes[i]
                del gis_response['states'][i]

        if len(sent_tx_hashes) > 0:
            if timeout <= elapsed:
                # timeout reached, terminate checking
                return False
            # Show some progress on the screen
            print('.')
            # Put on hold for polling_interval. Non-blocking, so you can
            # do other stuff in the meantime.
            await asyncio.sleep(polling_interval)
            elapsed = elapsed + polling_interval

    # All transactions in the bundle are confirmed
    return True


async def do_something() -> None:
    """
    While waiting for confirmation, you can execute arbitrary code here.
    """
    for _ in range(5):
        print('Doing something in the meantime...')
        await asyncio.sleep(2)


async def main() -> None:
    """
    A simple application that sends zero-value transactions to the Tangle and
    monitors the confirmation by the network. While waiting for the
    confirmation, we schedule a task (`do_something()`) to be executed concurrently.
    """
    # Transactions to be sent.
    transactions = [
        ProposedTransaction(
            address=addy,
            value=0,
            message=TryteString.from_unicode('First'),
        ),
        ProposedTransaction(
            address=addy,
            value=0,
            message=TryteString.from_unicode('Second'),
        ),
        ProposedTransaction(
            address=addy,
            value=0,
            message=TryteString.from_unicode('Third'),
        ),
    ]

    # Schedule coroutines as tasks, wait for them to finish and gather their
    # results.
    result = await asyncio.gather(
            send_and_monitor(transactions),
            # Send the same content. Bundle will be different!
            send_and_monitor(transactions),
            do_something(),
        )

    if not (result[0] and result[1]):
        print('Transactions did not confirm after %s seconds!' % timeout)
    else:
        print('All transactions are confirmed!')

if __name__ == '__main__':
    # Execute main() inside an event loop if the file is ran
    asyncio.run(main())
