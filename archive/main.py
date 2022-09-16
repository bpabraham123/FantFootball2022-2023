from data_cleaning import Data_Cleaning
import pandas as pd

def main():
    years = [2017, 2018, 2019, 2020, 2021]
    dc = Data_Cleaning(years)
    data = dc.join_qb_data()
    print(data)
    #data = dc.get_qb_data()
    #data.head()

if __name__ == '__main__':
    main()