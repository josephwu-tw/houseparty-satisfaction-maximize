from utils import *
import os
from dotenv import load_dotenv

load_dotenv('../.env')
guest_data_path = "../" + os.getenv("DATA_PATH") + "guest_list.csv"

guest_data = load_data(guest_data_path)

invite_num = guest_num_input()

dp = [0] * (invite_num + 1)



