# Vinci - June 2024

# Basically, we generate new wallet addresses on the TON blockchain.
# And feed the addresses to a free cloud mining site via scraping.
# And also keep a log of the addresses and their 24-word mnemonic.

from tonsdk.contract.wallet import WalletVersionEnum, Wallets
from tonsdk.utils import bytes_to_b64str
from tonsdk.crypto import mnemonic_new
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import yaml
import os
import random

config_data = 0
with open("config.yml", "r") as f:
    # config_data = yaml.full_load(f)
    config_data = yaml.safe_load(f)

MAX = config_data.get('Max')
URL = config_data.get('Url')
CURR_COUNT = config_data.get('Curr_Count')
PASSWORD = config_data.get('Password')


# Add one to the previous run
CURR_COUNT += 1

if not os.path.isfile("wallets.txt"):
    CURR_COUNT = 0

proxies = [
        #"52.13.248.29:3128",
        #"44.226.167.102:3128",
        # "167.102.133.111:80",
        #"35.161.172.205:3128",
        #"44.219.175.186:80",
        #"198.49.68.80:80",
        "35.185.196.38:3128",
        # "123.30.154.171:7777",
        #"3.141.217.225:80",
        # "52.35.240.119:1080",
        # "3.136.29.104:3128",
        # "20.111.54.16:8123",
        # "51.89.73.162:80",
        ]

def change_proxy():
    return random.choice(proxies)

def login(wallet_addr):
    proxy = change_proxy()

    chrome_options = Options()
    # chrome_options.add_argument('--headless=new')
    chrome_options.add_argument(f'--proxy-server={proxy}')

    print(f"Using Proxy: {proxy}...")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(URL)
    except:
        login(wallet_addr)

    time.sleep(3)

    try:
        wallet = driver.find_element(by=By.NAME, value='wallet').send_keys(wallet_addr)
        form = driver.find_element(by=By.XPATH, value='//*[@id="start"]/form')
        driver.execute_script("arguments[0].scrollIntoView();", form)
        time.sleep(1)

        button = driver.find_element(by=By.XPATH, value='//*[@id="start"]/form/div/button')
        button.click()
        # time.sleep(5)

        # If dashboard shows, we're logged in
        # Throws a NoSuchElementException
        # dashboard = driver.find_element(by=By.XPATH, value='/html/body/div[1]/header/div[2]/div/div/nav/ul/li[1]/a')
    except:
        login(wallet_addr)

        time.sleep(3)
    driver.close()

wallet_workchain = 0
wallet_version = WalletVersionEnum.v4r2
# wallet_mnemonics = mnemonic_new()

file_out = open("wallets.txt", "a")

while CURR_COUNT < MAX:
    # wallet_mnemonics = mnemonic_new()
    # _mnemonics, _pub_k, _priv_k, wallet = Wallets.from_mnemonics(wallet_mnemonics, wallet_version, wallet_workchain)

    _mnemonics, _pub_k, _priv_k, wallet = Wallets.create(wallet_version, wallet_workchain, PASSWORD)

    # Deploy External 
    query = wallet.create_init_external_message()
    base64_boc = bytes_to_b64str(query["message"].to_boc(False))

    address = wallet.address.to_string(True, True, False)

    login(address)

    print(f"Created Wallet #{CURR_COUNT}...")
    print(f"Wallet #{CURR_COUNT} Mining At {address}...")


    file_out.write(f"""\n
Wallet #{CURR_COUNT}
Address: {address}
Seed Phrase: {_mnemonics}
""")

    config_data['Curr_Count'] = CURR_COUNT
    with open("config.yml", "w") as f:
        yaml.dump(config_data, f, sort_keys=False)

    print(f"Wallet #{CURR_COUNT} Backed Up Successfully...")

    CURR_COUNT += 1

file_out.close()


