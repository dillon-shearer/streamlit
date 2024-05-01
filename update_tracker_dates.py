import pandas as pd
import streamlit as st
import numpy as np

def show():
    # Function to read the Users.csv file
    def read_users_csv(file_path):
        return pd.read_csv(file_path)

    # Function to get data from Google Sheet and extract the ID column
    def get_google_sheet_data(sheet_url):
        # Read the Google Sheet
        df_sheet = pd.read_csv(sheet_url, encoding='UTF-8')
        # Extract the ID column
        id_column = df_sheet['ID']
        return id_column

    # Function to merge data from Users.csv based on ID
    def merge_data(users_df, id_column):
        # Select the required columns from Users.csv
        columns_to_select = ['ID', 'Verified Date', 'User Sign Date', 'Auth. Business Official Sign Date', 'Answer ALS Official Sign Date']
        selected_data = users_df[columns_to_select]
        # Merge based on the ID column
        merged_data = pd.merge(id_column, selected_data, on='ID', how='left')
        return merged_data

    # Function to format the date columns
    def format_dates(df):
        date_columns = ['Verified Date', 'User Sign Date', 'Auth. Business Official Sign Date', 'Answer ALS Official Sign Date']
        for column in date_columns:
            df[column] = pd.to_datetime(df[column]).dt.strftime('%Y-%m-%d')
        return df

    # Function to extract the most recent collaborator signature date
    def extract_recent_collab_signature(cell):
        if pd.isna(cell):
            return "No collaborators"
        
        entries = cell.split(';')
        sign_dates = []
        for entry in entries:
            if "Sign Status: Sent" in entry:
                return np.nan
            if "Sign Date:" in entry:
                sign_date = entry.split(': ')[1].strip()
                sign_dates.append(pd.to_datetime(sign_date))
        
        if sign_dates:
            return max(sign_dates).strftime('%Y-%m-%d')
        else:
            return np.nan

    st.title("Users Data")

    # File upload for Users.csv
    users_csv_file = st.file_uploader("Upload Users.csv", type=["csv"])

    if users_csv_file is not None:
        # Read the Users.csv file
        users_df = read_users_csv(users_csv_file)

        # Google Sheet URL
        sheet_url = "https://docs.google.com/spreadsheets/d/1JPi2raTk0cXK3X2fvVtsFiSXtbzX7lRU1btjjodn10w/export?format=csv&gid=1579761793"
            
        # Get data from Google Sheet
        df = pd.read_csv(sheet_url, encoding='UTF-8')

        df_id = df[['ID', 'Email']]

        users_df = users_df[['Email', 'ID' 'Verified Date', 'User Sign Date', 'Auth. Business Official Sign Date', 'Answer ALS Official Sign Date', 'Collaborators']]
        
        # Rename the 'Id' column to 'ID' in the users_df DataFrame
        users_df.rename(columns={'Id': 'ID'}, inplace=True)

        # Merge df_id and users_df on the column 'ID', keeping all rows from users_df
        merged_df = df_id.merge(users_df, on='ID', how='left')

        # Apply the function to extract the most recent collaborator signature date
        merged_df['Last Collaborator Signature'] = merged_df['Collaborators'].apply(extract_recent_collab_signature)

        st.write(merged_df)

        # Drop the 'ID' and 'Email' columns from merged_df
        merged_df = merged_df.drop(columns=['ID'])

        # Define function for cleaning datetime values
        def clean_datetime(value):
            if isinstance(value, str):
                return value.split('T')[0]
            else:
                return value

        # Columns to clean
        columns_to_clean = ['Verified Date', 'User Sign Date', 'Auth. Business Official Sign Date', 'Answer ALS Official Sign Date']

        # Apply the clean_datetime function to all specified columns
        merged_df[columns_to_clean] = merged_df[columns_to_clean].applymap(clean_datetime)

        st.write(merged_df)