def guest_num_input():
    while True:
        try:
            num_guests = int(input("Enter the number of guests: "))
            if num_guests <= 0:
                print("Please enter a positive integer.")
                continue
            return num_guests
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def save_data(df, path):
    while True:
        save_options = input(f"Do you want to save the data to {path}? (y/n): ").strip().lower()

        if save_options == 'y':
            try:
                df.to_csv(path, index=False)
                print(f"Data saved to {path}")
                break
            except Exception as e:
                print(f"Error saving data: {e}")
                path = input("Please enter a valid file path to save the data: ")
        else:
            print("Data is dropped.")
            break

def load_data(path):
    import pandas as pd
    try:
        df = pd.read_csv(path)
        print(f"Data loaded from {path}")
        print("")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None