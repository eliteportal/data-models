# update EL model from data dictionary
import pandas as pd


def main():
    url = "https://raw.githubusercontent.com/Sage-Bionetworks/ELITE_data_dictionary/main/EL.data.model.csv"
    df = pd.read_csv(url)
    df.to_csv("EL.data.model.csv", index=False)


if __name__ == "main":
    main()
