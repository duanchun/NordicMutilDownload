from pynrfjprog import API
from pynrfjprog import LowLevel

def eraseAll():
    try:
        api = API.API('NRF52')
        api.open()
        api.connect_to_emu_without_snr()
        api.erase_all()
        api.close()
    except LowLevel.APIError :
        print("Error %s",LowLevel.APIError)
    print("End")

if __name__ == '__main__':
    eraseAll()
