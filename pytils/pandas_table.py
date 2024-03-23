import pandas
from pandas import ExcelWriter


def create_excel_table(dataframe, workbook, sheet_name='Sheet1'):
    """
    Create an Excel table from a pandas dataframe and write it to xlsxwriter workbook.

    Parameters:
    dataframe (pandas.DataFrame): The dataframe to be written to the Excel file.
    workbook (xlsxwriter.workbook.Workbook): The xlsxwriter workbook to write to.
    sheet_name (str): The name of the Excel sheet. Default is 'Sheet1'.

    Returns:
    xlsxwriter.workbook.Workbook: The updated xlsxwriter workbook.
    """
    # Ensure the index has a name
    if not dataframe.index.name:
        dataframe.index.name = 'Index'

    # Reset index to allow inserting a user defined header
    if dataframe.index.name not in dataframe.columns:
        dataframe = dataframe.reset_index()

    # Write the dataframe to the Excel workbook
    dataframe.to_excel(workbook, sheet_name=sheet_name, startrow=1, header=False, index=False)

    # Get the xlsxwriter workbook and worksheet objects
    worksheet = workbook.sheets[sheet_name]

    # Get the dimensions of the dataframe
    (max_row, max_col) = dataframe.shape

    # Create a list of column headers, to use in add_table()
    column_settings = [{'header': column} for column in dataframe.columns]

    # Add the Excel table structure. Pandas will add the data.
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings, 'name': sheet_name})

    # Make the columns wider for clarity
    worksheet.set_column(0, max_col - 1, 12)

    return workbook
