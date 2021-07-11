# CryptoSway
 Python that sends effects to a LED strip ws2912b informing the mining status using Raspberry Pi and mining via NiceHash.



1. Use a ws2812b led strip on pin 18
2. Edit ADDR_BTC in 'config.py'
3. Open 'mining_status_w2812b_rpi.py'

Requests to:
https://api2.nicehash.com/main/api/v2/mining/external/ADDR_BTC/rigs2
https://api.binance.com/api/v3/ticker/price?symbol=BTCBRL