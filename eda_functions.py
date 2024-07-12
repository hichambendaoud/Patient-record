import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_csv(file_path, delimiter=',', encoding='utf-8'):
    """
    Load a CSV file with the specified delimiter and encoding.
    Returns:
    - df: DataFrame, loaded DataFrame
    """
    df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
    return df

def handle_duplicates(df, duplicates_file_path):
    """Save duplicated rows to a file and return a DataFrame without duplicates."""
    duplicated_df = df[df.duplicated()]
    df_cleaned = df.drop_duplicates()
    
    if not duplicated_df.empty:
        save_dataframe(duplicated_df, duplicates_file_path)
        print(f"Removed {len(duplicated_df)} duplicate rows. Duplicates saved to {duplicates_file_path}.")
    else:
        print("No duplicate rows found.")
    
    return df_cleaned

def save_missing_values_info(df, file_path):
    """Save columns with missing values and their counts to a CSV file."""
    missing_info = df.isnull().sum()
    missing_info = missing_info[missing_info > 0].reset_index()
    missing_info.columns = ['Column', 'Missing Values Count']
    missing_info.to_csv(file_path, index=False)
    print(f"Missing values information saved to {file_path}.")

def save_rows_with_missing_values(df, file_path):
    """Save rows with missing values in columns that contain missing values to a CSV file."""
    columns_with_missing = df.columns[df.isnull().any()]
    rows_with_missing = df[df.isnull().any(axis=1)].index
    df_missing = df.loc[rows_with_missing, columns_with_missing]
    df_missing.to_csv(file_path, index=False)
    print(f"Rows with missing values saved to {file_path}.")
    return df_missing

def fillna_with_prefix(df):
    """
    Fill missing values in the 'GENDER' column using the 'PREFIX' column.
    'Mrs.', 'Ms.' -> 'female'
    'Mr.' -> 'male'
    """
    # Define a mapping from PREFIX to GENDER
    prefix_to_gender = {
        'Mrs.': 'F',
        'Ms.': 'F',
        'Mr.': 'M'
    }
    
    # Apply the mapping to fill missing values in the GENDER column
    df['GENDER'] = df.apply(
        lambda row: prefix_to_gender[row['PREFIX']] if pd.isnull(row['GENDER']) else row['GENDER'],
        axis=1
    )
    return df

def clean_dates(df, date_columns):
    """
    Clean and convert specified date columns to datetime format.
    
    Parameters:
    - df: DataFrame
    - date_columns: Dictionary where keys are column names and values are the date formats
      e.g., {'BIRTHDATE': '%Y-%m-%d', 'DEATHDATE': '%Y-%m-%d'}
    """
    for column, date_format in date_columns.items():
        if column in df.columns:
            # Replace '|' with '-' if necessary
            df[column] = df[column].astype(str).str.replace('|', '-')
            
            # Convert to datetime with specified format
            df[column] = pd.to_datetime(df[column], format=date_format, errors='coerce')
    
    return df
# Visualisation 
def plot_boxplot(df, column, title):
    """Plot a boxplot for a given column."""
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=df[column])
    plt.title(title)
    plt.xlabel(column)
    plt.show()

def plot_boxplots(df, columns, title):
    """
    Plot boxplots for given columns in subplots.
    
    Parameters:
    - df: DataFrame
    - columns: List of column names to plot
    - title: Title for the entire plot
    """
    n = len(columns)
    fig, axes = plt.subplots(n, 1, figsize=(8, 4 * n))

    for i, column in enumerate(columns):
        sns.boxplot(x=df[column], ax=axes[i])
        axes[i].set_title(f'Boxplot of {column}')
        axes[i].set_xlabel(column)
    
    plt.tight_layout()
    plt.suptitle(title, y=1.02, fontsize=16)
    plt.show()

def replace_missing_values(df, placeholder="Unknown"):
    """Replace missing values with a placeholder in the DataFrame."""
    df = df.fillna(placeholder)
    return df

# Outliers 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def save_dataframe(df, file_path):
    """Save the DataFrame to a CSV file."""
    df.to_csv(file_path, index=False)
    print(f"DataFrame saved to {file_path}.")

def filter_outliers_and_save(df, column, outliers_file_path):
    """
    Identify outliers in the specified column, save them to a CSV file, 
    and mark outliers as NaN in the DataFrame.
    
    Parameters:
    - df: DataFrame
    - column: Column name to check for outliers
    - outliers_file_path: Path to save the outliers DataFrame
    
    Returns:
    - df_cleaned: DataFrame with outliers marked as NaN
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    # Define bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Identify outliers
    outliers_df = df[(df[column] < lower_bound) | (df[column] > upper_bound)]

    # Mark outliers as NaN in the original DataFrame
    df_cleaned = df.copy()
    df_cleaned.loc[(df_cleaned[column] < lower_bound) | (df_cleaned[column] > upper_bound), column] = pd.NA

    if not outliers_df.empty:
        save_dataframe(outliers_df, outliers_file_path)
        print(f"Identified {len(outliers_df)} outlier rows. Outliers saved to {outliers_file_path}.")
    else:
        print("No outlier rows found.")
    
    return df_cleaned
#= = == = = = = =  = =

def save_dataframe(df, file_path):
    """Save the DataFrame to a CSV file."""
    df.to_csv(file_path, index=False)
    print(f"DataFrame saved to {file_path}.")

def display_info(df):
    """Display basic information about the DataFrame."""
    print("DataFrame Info:")
    print(df.info())

def display_description(df):
    """Display descriptive statistics of the DataFrame."""
    print("Descriptive Statistics:")
    print(df.describe())

def select_numeric_columns(df):
    return df.select_dtypes(include=[np.number])

def display_correlation(df):
    numeric_df = select_numeric_columns(df)
    print("Correlation Matrix:")
    print(numeric_df.corr())

# Visaul