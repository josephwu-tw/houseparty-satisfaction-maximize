import pandas as pd
import numpy as np
import random
from dotenv import load_dotenv
import os
from methods.utils import guest_num_input, save_data

load_dotenv()

food_list = os.getenv("FOOD_LIST").split(",")
beverage_list = os.getenv("BEVERAGE_LIST").split(",")
columns = food_list + beverage_list + ["Intimacy Level"]

save_path = os.getenv("DATA_PATH") + "guest_list.csv"

def generate_guest_list(num_guests):
    guest_data = []
    for _ in range(num_guests):
        temp = []
        for _ in range(len(columns)-1):
            temp.append(random.randint(1, 5))

        temp.append(random.randint(1, 10))  # Intimacy Level
        guest_data.append(temp)

    df = pd.DataFrame(guest_data, columns=columns)
        
    return df

if __name__ == "__main__":
    num_guests = guest_num_input()
    
    print("Generating guest list...")
    guest_df = generate_guest_list(num_guests)
    print("")
    print("Guest list generated.")
    print(guest_df.head())
    print("")
    save_data(guest_df, save_path)
    
    





