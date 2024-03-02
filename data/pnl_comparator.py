import warnings
warnings.filterwarnings("ignore")

# this should have one main test case file which will have multiple sheets in the data_pnl_main_excel folder
import glob
# rename "..//data_pnl_main_excel/*.xlsx" to "BASE_POST_Automation/SPG"

from datetime import date
import pandas as pd

# Get today's date
today = date.today()

# Format the date as a string
today_str = today.strftime("%d-%B-%Y")
    
columns = ['Revenue','RETAIL (ALL)', 'Primary CVS', 'Primary NON-CVS (CAPPED)', 'Primary NON-CVS (NON-CAPPED)', 
           'Secondary CVS', 'Secondary NON-CVS (CAPPED)', 'Secondary NON-CVS (NON-CAPPED)',
           'Specialty CVS', 'Specialty NON-CVS (CAPPED)', 'Specialty NON-CVS (NON-CAPPED)',
           'Mail(All) MAIL/MC', 'Mail(All) MAIL', 'Mail(All)  MAINTENANCE CHOICE']


columns_agg = ['Revenue', 'Current RETAIL', 'Current MAIL', 'Current SPECIALTY', 'Current REBATES', 'Current TOTAL',
              'Year 1 RETAIL', 'Year 1 MAIL', 'Year 1 SPECIALTY', 'Year 1 REBATES', 'Year 1 TOTAL',
              'Year 2 RETAIL', 'Year 2 MAIL', 'Year 2 SPECIALTY', 'Year 2 REBATES', 'Year 2 TOTAL',
              'Year 3 RETAIL', 'Year 3 MAIL', 'Year 3 SPECIALTY', 'Year 3 REBATES', 'Year 3 TOTAL']

columns_agg_prospect = ['Revenue', 
              'Year 1 RETAIL', 'Year 1 MAIL', 'Year 1 SPECIALTY', 'Year 1 REBATES', 'Year 1 TOTAL',
              'Year 2 RETAIL', 'Year 2 MAIL', 'Year 2 SPECIALTY', 'Year 2 REBATES', 'Year 2 TOTAL',
              'Year 3 RETAIL', 'Year 3 MAIL', 'Year 3 SPECIALTY', 'Year 3 REBATES', 'Year 3 TOTAL']
              
              
cols = [str(i)+" Difference (%)" for i in range(1, 14)]
cols_21 = [str(i)+" Difference (%)" for i in range(1, 21)]

def color_recommend(s):
    try:
        return np.where(abs(float(s)) > threshold,
                    'background-color: yellow; color: red',
                    'background-color: white')
    except:
        return
        
def color_negative_red(value):
    
    threshold = 1
    try:
        if float(value) > threshold:
            color = 'yellow'
        else:
            color = 'white'
            return
        return f'background-color: {color}'
    except:
        try:
            if abs(float(str(value).replace(")", "").replace("(", "").replace(" ", "").rstrip().lstrip())) > threshold:
                return f'color: red;background-color:yellow'
            else:
                return f'color: red'
        except:
            return
        return
        
# Function to apply yellow background to cells in columns "A" and "B" with values less than 0
def highlight_negative_14(column):
    
    if column.name in cols:
        # Use pd.to_numeric to convert values to numeric (if possible)
        numeric_column = pd.to_numeric(column, errors="coerce")
        
        # Check if a value is numeric and meets the condition
        return ['background-color: yellow; color: red' if pd.notna(val) and abs(round(val, 4)) > 1 else '' for val in numeric_column]
    else:
        return [''] * len(column)
    
def highlight_negative_21(column):
    
    if column.name in cols_21:
        # Use pd.to_numeric to convert values to numeric (if possible)
        numeric_column = pd.to_numeric(column, errors="coerce")
        
        # Check if a value is numeric and meets the condition
        return ['background-color: yellow; color: red' if pd.notna(val) and abs(round(val, 4)) > 1 else '' for val in numeric_column]
    else:
        return [''] * len(column)
        
def transform(table1):
    
    try:
        get_value_index = table1[table1['Revenue'] == '% Brand / % Generic Spend'].index
        get_value = table1[table1['Revenue'] == '% Brand / % Generic Spend'].values.tolist()
        table1.loc[table1['Revenue'] == '% Brand / % Generic Spend'] = 0
    except Exception as e:
        print(e)
        pass
    
    #transform values into string and add parenthesis when they are negative
    for c in table1.columns[1:]:
        try:
            table1[c] = table1[c].astype(float).round(4)
        except:
            pass
    
        table1[c] = table1[c].astype(str).apply(lambda x: f"({abs(float(x))})" if str(x) not in ["", "Pass", "Fail"] and float(x) < 0 else x)
    
    try:
        table1.loc[get_value_index] = get_value
    except:
        pass
    
    table1 = table1.replace('-0.0',"0.0", regex=True)
    return table1

def start_matching(base, mpg, aggregated=False, columns=None, type_of_files=None):
    
    if type_of_files == "aggregate":
        if "prospect" in base:
            skiprows = 2
            columns = columns
        else:
            skiprows = 3
            columns = columns
    elif type_of_files == "network":
        skiprows = 3
        columns = columns
    else:
        columns = columns_agg
        skiprows = 2
    
    # Base file
    base = pd.read_csv(base, skiprows=skiprows)
    # Post file
    mpg = pd.read_csv(mpg, skiprows=skiprows)
    
    try:
        base.columns = columns
        mpg.columns = columns
    except:
        try:
            base.columns = columns_agg_prospect
            mpg.columns = columns_agg_prospect
            columns = columns_agg_prospect
        except:
            base.columns = columns
            mpg.columns = columns
        
    base_bkp = base.copy()
    mpg_bkp = mpg.copy()

    
    result_df = base[[columns[0]]]
    
    for i in range(1, len(columns)):
        
        base_col = pd.to_numeric(base_bkp[columns[i]], errors='coerce')
        post_col = pd.to_numeric(mpg_bkp[columns[i]], errors='coerce')

        result_df["base " + columns[i]] = base_col.fillna(base_bkp[columns[i]])
        result_df["post " + columns[i]] = post_col.fillna(mpg_bkp[columns[i]])
        
        difference = []
        percent_diff = []
        for k in range(len(result_df["post " + columns[i]].values)):
            try:
                diff = result_df["post " + columns[i]].values[k] - result_df["base " + columns[i]].values[k]
                try:
                    per_diff = diff / result_df["base " + columns[i]].values[k]
                except:
                    per_diff = 0
                per_diff = per_diff * 100
                difference.append(diff)
                percent_diff.append(per_diff)
            except Exception as e:
                diff = result_df["post " + columns[i]].values[k] == result_df["base " + columns[i]].values[k]
                per_diff = result_df["post " + columns[i]].values[k] == result_df["base " + columns[i]].values[k]
                difference.append(diff)
                percent_diff.append(per_diff)
        
        result_df[str(i) + ' Difference'] = difference
        result_df[str(i) + ' Difference (%)'] = percent_diff
    
    result_df = result_df.fillna(0)
    result_df = transform(result_df)
    result_df_copy = result_df.copy()
    
    # Apply the function to the DataFrame and set the CSS properties
    if aggregated is False:
        result_df = result_df.style.applymap(color_negative_red, subset=[i for i in cols if "%" in i or "Difference" in i]).applymap(color_recommend, subset=[i for i in cols if "%" in i or "Difference" in i])
    else:
        result_df = result_df.style.applymap(color_negative_red, subset=[i for i in cols_21 if "%" in i or "Difference" in i]).applymap(color_recommend, subset=[i for i in cols_21 if "%" in i or "Difference" in i])
        
    return result_df, result_df_copy



def compare_pnl(base=None, post=None, type_of_files="raw"):

    """
    base: the complete path of BASE file
    base: the complete path of POST file
    type_of_files: --> "None" (for comparing default PNLs in ../data folder)
                   --> "raw" (for comparing raw PNLs)
                   --> "network" (for comparing raw PNLs)
                   --> "aggregate" (for comparing raw PNLs)
    """
    
    read_default = False
    
    if base is None and post is None:
        print("data will be read from folder {../data/}")
        read_default = True
    
    elif base is None and post is not None:
        print("Please provide BASE file path")
        return "Please provide BASE file path"
    
    elif base is not None and post is None:
        print("Please provide POST file path")
        return "Please provide POST file path"
    else:
        pass
    
    aggregate_base = None
    aggregate_post = None
    network_base = None
    network_post = None
        
    if read_default is True:
        files = glob.glob("..//data/*base*.xlsx") + glob.glob("..//data/*post*.xls") + glob.glob("..//data/*base*.csv") + glob.glob("..//data/*post*.csv")
        files = [i for i in files if "~" not in i]

        try:
            aggregate_base = [i for i in files if "base" in i.lower() and "aggregate" in i.lower()][0]
            aggregate_post = [i for i in files if "post" in i.lower() and "aggregate" in i.lower()][0]
            file_name_to_save_results = "../output_report/"+"aggregate_comparison"+"_"+today_str+"_results.xlsx"
            print(f"Results will save to {file_name_to_save_results}")
        except:
            pass

        try:
            network_base = [i for i in files if "base" in i.lower() and "network" in i.lower()][0]
            network_post = [i for i in files if "post" in i.lower() and "network" in i.lower()][0]
            file_name_to_save_results = "../output_report/"+"network_comparison"+"_"+today_str+"_results.xlsx"
            print(f"Results will save to {file_name_to_save_results}")
        except:
            aggregate_base = [i for i in files if "base" in i.lower()][0]
            aggregate_post = [i for i in files if "post" in i.lower()][0]
            file_name_to_save_results = "../output_report/"+"Base_Post_Raw_comparison"+"_"+today_str+"_results.xlsx"
            print(f"Results will save to {file_name_to_save_results}")
            pass
    else:
        if type_of_files == "raw":
            aggregate_base = base
            aggregate_post = post
            file_name_to_save_results = "../output_report/"+"Base_Post_Raw_comparison"+"_"+today_str+"_results.xlsx"
        elif type_of_files == "aggregate":
            aggregate_base = base
            aggregate_post = post
            file_name_to_save_results = "../output_report/"+"aggregate_comparison"+"_"+today_str+"_results.xlsx"
        else:
            network_base = base
            network_post = post
            file_name_to_save_results = "../output_report/"+"network_comparison"+"_"+today_str+"_results.xlsx"
        
    temp = pd.DataFrame(data=[["","","","","","","","","","","Raw Comparison","","","","","","","","",""],
                                 ["","","","","","","","","","","Base vs Post","","","","","","","","",""]]).style.set_properties(**{'background-color': 'lightblue'})
    
    store_all_sheets = []
    
    if type_of_files == "network":
        res, result_df_copy = start_matching(network_base, network_base, columns=columns, type_of_files=type_of_files)
        store_all_sheets.append([temp, res])

    elif type_of_files == "aggregate":
        res, result_df_copy = start_matching(aggregate_base, aggregate_post, columns=columns_agg, type_of_files=type_of_files)
        store_all_sheets.append([temp, res])

    else:
        print("Network Comparison")
        res, result_df_copy = start_matching(aggregate_base, aggregate_post, columns=columns, type_of_files=type_of_files)
        store_all_sheets.append([temp, res])
   
    display(res)
    
    last_loc = 1

    print(f"Report Save to {file_name_to_save_results}")
    # Store DataFrames for Saving
    # create a excel writer object
    with pd.ExcelWriter(file_name_to_save_results, engine="openpyxl") as writer:
        for i in store_all_sheets:
            for j in i:
                j.to_excel(writer, index=False, startrow=last_loc, startcol=1)
                try:
                    last_loc = last_loc + 2 + j.shape[0]
                except:
                    last_loc = last_loc + 2 + j.data.shape[0]