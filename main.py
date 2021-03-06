import csv
import pandas
import sys

def identifyquery(args):
    if len(args) <= 2:
        return 0

    inputlength = len(args)

    csvdata = pandas.read_csv(str(args[2]))
    csvdata = csvdata.convert_dtypes()
    limit = 0

    # FROM Query
    # which has 'FROM' as the 1st argument and length as 3 including the main.py file name
    if inputlength == 3:
        if args[1] == 'FROM':
            printheader(csvdata)
            return printrows(csvdata, 0, len(csvdata))
        else:
            return 0
    
    # SELECT Query
    # which has 'SELECT' as the 1st argument and length as > 3 including the main.py file name
    if (inputlength > 3) and (args[3] == 'SELECT'):
        # Validating Columns to print
        res = printselectedcolumns(csvdata, inputlength, args)
        my_df = pandas.DataFrame(res)
        my_df.to_csv('my_csv.csv',index=False, header=False)
        csvdata = pandas.read_csv('my_csv.csv')
        csvdata = csvdata.convert_dtypes()

        if inputlength > 5 and args[5] == 'ORDERBY':
            args[3] = 'ORDERBY'
            args[4] = args[6]
            if inputlength > 7: args[5] = args[7]
        elif args[inputlength-2] == 'TAKE':
            limit = int(args[inputlength-1])

            if limit < 0: return 0
            if limit > len(csvdata): limit = len(csvdata)
            
            csvdata = csvdata[0:limit + 1].copy()
            printheader(csvdata)
            return printrows(csvdata, 0, limit)
        elif inputlength > 4:
            printheader(csvdata)
            return printrows(csvdata, 0, len(csvdata))

    # TAKE Query
    # which has 'TAKE' as the 3rd argument and length as 5 including the main.py file name
    if (inputlength == 5) and (args[3] == 'TAKE'):
        limit = int(args[4])
        if limit < 0: return 0
        if limit > len(csvdata): limit = len(csvdata)
        printheader(csvdata)
        return printrows(csvdata, 0, limit)

    # ORDERBY Query
    # which has 'ORDERBY' as the 3rd argument and length as > 4 including the main.py file name
    if (inputlength > 4) and (args[3] == 'ORDERBY'):
        # Checking if the query contains TAKE(limit on number of output rows)
        if args[inputlength - 2] == 'TAKE':limit = int(args[inputlength - 1])
        if limit == 0 or limit > len(csvdata): limit = len(csvdata)
        if args[4] not in csvdata.columns.values.tolist():
            print(args[4] + " is not a valid column name")
            return 0

        # sort in descending order based on the input column
        if inputlength > 5 and args[5] == 'DESC':
            csvdata.sort_values(args[4], ascending=False, ignore_index=True, inplace=True)
        else:
            csvdata.sort_values(args[4], ascending=True, ignore_index=True, inplace=True)
        printheader(csvdata)
        return printrows(csvdata, 0, limit)

    # JOIN Query
    # which has 'JOIN' as the 3rd argument and length as > 4 including the main.py file name
    if (inputlength > 4) and (args[3] == 'JOIN'):
        # Merge CSV files to join the columns
        file2 = pandas.read_csv(args[4])
        file2 = file2.convert_dtypes()
        csvdata = pandas.merge(csvdata, file2, left_on=args[5], right_on=args[5], how='left')
        # Merge 3rd CSV file to join the column if exists
        if inputlength > 7:
            file3 = pandas.read_csv(args[7])
            file3 = file3.convert_dtypes()
            csvdata = pandas.merge(csvdata, file3, how='left', on=args[5])
        printheader(csvdata)
        return printrows(csvdata, 0, len(csvdata))

    # COUNTBY Query
    # which has 'COUNTBY' as the 3rd argument and length as > 4 including the main.py file name
    if (inputlength > 4) and (args[3] == 'COUNTBY'):
        limit = 0
        # Limit the output rows if TAKE Clause exists
        if inputlength > 7:
            if args[7] == 'TAKE': limit = int(args[8])
        # Count the columns by grouping on the input column name
        csvdata = csvdata.groupby(args[4]).size().reset_index(name='count')
        # Order the output by count and then by the input column name if same count exists for 2 rows
        if (inputlength > 5) and (args[5] == 'ORDERBY'):
            csvdata.sort_values(['count', args[4]], ascending=False, ignore_index=True, inplace=True)
        if limit == 0 : limit = len(csvdata)
        printheader(csvdata)
        return printrows(csvdata, 0, limit)
    return 0

# Reusable Code to print the rows of the query results from CSV file
def printrows(csvdata, startrow, endrow):
    # Initializing the List containing the Column Names of the query results
    columns = []
    # Adding column Names to the list from the input CSV file data
    for columnName in csvdata:
        columns = columns + [columnName]
    result = []
    # Iterating to print each row and each column value
    for row in range(startrow, endrow):
        list = []
        for index in range(len(columns)):
            # If current index is not the last column, add ',' between the columns
            if index < len(columns) - 1:
                print(csvdata.loc[row, columns[index]], end='')
                print(",", end='')
            # else skip ', and move to next line
            else:
                print(csvdata.loc[row, columns[index]])
            list = list + [csvdata.loc[row, columns[index]]]
        result = result + [list]
    return result

# Code to print the rows with the selected columns from the input
def printselectedcolumns(csvdata,inputlength,args):
    # print header columns specified in the input arguments
    #for index in range(4, inputlength):
    #    if index < inputlength - 1:
    #        print(args[index], end='')
    #        print(",", end='')
    #    else:
    #        print(args[index])
    result = []
    # print each row with the column names specified in the input arguments
    columns = args[4].split(",")
    if args[4] == '*':
        columns = csvdata.columns.values.tolist()
    result += [columns]
    for row in range(len(csvdata)):
        list = []
        for index in range(0, len(columns)):
       #     if index < len(columns) - 1:
       #         print(csvdata.loc[row, columns[index]], end='')
       #         print(",", end='')
       #     else:
       #         print(csvdata.loc[row, columns[index]])
            list = list + [csvdata.loc[row, columns[index]]]
        result = result + [list]
    return result


# Method to print the first row of the output, which has the Column Names of the output
def printheader(data):
    count = 0
    result = []
    for col in data:
        if count < len(data.axes[1])-1:
            print(col, end='')
            print(",", end='')
        else:
            print(col)
        result = result + [col]
        count = count + 1
    return result


# Entry point of the project
identifyquery(sys.argv)
