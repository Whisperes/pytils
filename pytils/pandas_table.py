import pandas
from pandas import ExcelWriter

def create_excel_table(df, wr, sheet_name = 'Sheet1'):
    if not df.index.name:
        df.index.name = 'Index'

    # index and skip one row to allow us to insert a user defined header.
    if df.index.name not in df.columns:
        df = df.reset_index()
    df.to_excel(wr, sheet_name=sheet_name, startrow=1, header=False, index=False)

    # Get the xlsxwriter workbook and worksheet objects.
    worksheet = wr.sheets[sheet_name]

    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Create a list of column headers, to use in add_table().
    column_settings = [{'header': column} for column in df.columns]

    # Add the Excel table structure. Pandas will add the data.
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings, 'name': sheet_name})

    # Make the columns wider for clarity.
    worksheet.set_column(0, max_col - 1, 12)
    return wr
