import json
import xlsxwriter

def writeToXLSX(sheet, obj, row=1, column=0):

    if type(obj) is dict:
        # Iterate over the dict writing the value to the column to the right, 
        # and the key in the current column for each new row added
        totalAddedRows = 0
        for key, value in obj.items():
            addedRows = writeToXLSX(sheet, value, row + totalAddedRows, column + 1)
            for i in range(addedRows):
                sheet.write(row + totalAddedRows + i, column, str(key))
            totalAddedRows += addedRows
        return totalAddedRows
    elif type(obj) is list:
        # Iterate over the list writing each element to the column to the right, 
        # and the index in the current column for each new row added
        totalAddedRows = 0
        for i in range(len(obj)):
            element = obj[i]
            addedRows = writeToXLSX(sheet, element, row + totalAddedRows, column + 1)
            for f in range(addedRows):
                sheet.write(row + totalAddedRows + f, column, i)
            totalAddedRows += addedRows
        return totalAddedRows
    else:
        # Base case: int/str/bool/null
        # Write the value to the current cell
        sheet.write(row, column, str(obj))
        return 1