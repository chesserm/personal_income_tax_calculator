import sys
from collections import OrderedDict

# Calculates the Adjusted Gross Income
def calculateAGI(total_income, atl_deductions):
    '''
    Inputs:
    - total_income: This is the total income
    - atl_deductions: Above the Line deductions (dictionary)

    Outputs:
    - AGI: Adjusted Gross Income (your total income minus above-the-line deductions)
    '''

    # Sum up all of the above the line deductions
    # e.g. 401(k) contributions, IRA contributions, health savings account contributions, etc
    sum_atl_deductions = 0.0
    for deduction_name,deduction_amount in atl_deductions.items():
        sum_atl_deductions += deduction_amount

    # AGI is your total income minus your above the line deductions
    agi = total_income - sum_atl_deductions

    return agi


# Calculates the amout of fica tax owed
def calculateFICAAmountsOwed(total_income, filing_status, fica_taxes, medicare_surtax_limits):
    '''
    Input: 
    - total_income: Total income (salary)
    - fica_taxes: OrderedDict from the fica_taxes.csv file containing FICA tax info
    - medicare_surtax_limits: OrderedDict from the medicare_surtax.csv file containing salary limit
                              info for the medicare surtax application

    Output:
    - fica_amount_owed : The amount owed to the government based on FICA
    '''
    # Amount that can contribute to social security tax (read from file)
    max_ss_tax_info_file = open("csv_files/max_ss_tax_income_limit.csv", 'r')
    max_ss_tax_income_limit = float(max_ss_tax_info_file.readline())
    max_ss_tax_info_file.close()
    
    # The income amount at which the medicare surtax is applied
    min_medicare_surtax_income = 0.00

    # Filing status determines the min amount for medicare surtax income
    if (filing_status == 1):
        min_medicare_surtax_income = float(medicare_surtax_limits["Single"])
    else:
        min_medicare_surtax_income = float(medicare_surtax_limits["Jointly"])


    # Return value (amount of FICA tax owed)
    fica_amount_owed = 0.00

    # Find the amount of social security FICA tax owed
    if (total_income > max_ss_tax_income_limit):
        fica_amount_owed += max_ss_tax_income_limit * fica_taxes["Social Security"]
    else:
        fica_amount_owed += total_income * fica_taxes["Social Security"]


    # Find the amount of medicare tax owed
    fica_amount_owed += total_income * fica_taxes["Medicare Tax"]

    # Check if the salary is high enough to warrant needing to pay the medicare surtax
    if (total_income > min_medicare_surtax_income):
        fica_amount_owed += (total_income - min_medicare_surtax_income) * fica_taxes["Medicare Surtax"]
    
    return fica_amount_owed


# Calculates taxable income
def calculateTaxableIncome(agi, standard_deduction, itemized_deductions):
    '''
    Inputs: 
    - agi: adjusted gross income calculated by calculateAGI()
    - standard_deduction: The standard deduction amount
    - deductions: dictionary with k,v for itemized deductions
    
    Output:
    taxable_income : Taxable income (AGI - deductions)
    '''

    # Sum up the total of the itemized deductions
    sum_itemized_deductions = 0.0
    for deduction_name,deduction_amount in itemized_deductions.items():
        sum_itemized_deductions += deduction_amount

    # You will use the greater of the standardized deduction or itemized deduction
    deduction_used = max(standard_deduction, sum_itemized_deductions)

    # Calculate taxable income 
    taxable_income = agi - deduction_used

    return taxable_income


# Calculate federal tax
def calculateFederalTaxOwed(taxable_income, tax_brackets, tax_credits):
    '''
    Input: 
    - taxable_income: This is your final taxable income (output from calculateTaxableIncome() )
    - tax_brackets: This is a dictionary with keys as tax brackets and values as rates (decimal percentages)
    - tax_credits: This is a dictionary of tax credits (key is name of credit, value is amount of credit)

    Output:
    - federal_tax_owed : This is the amount of federal tax owed (federal tax liability)
    '''

    fed_tax_owed = 0.00
    previous_bracket_upper_value = 0.0

    
    for max_band_value, rate in tax_brackets.items():
        max_band_value = int(max_band_value)

        # If the taxable income is greater than the upper limit of the bracket
        # Then the entirity of the bracket must be paid 
        if (taxable_income > max_band_value):
            amount_paid_at_this_bracket = (max_band_value - previous_bracket_upper_value) * rate
            fed_tax_owed += amount_paid_at_this_bracket
            previous_bracket_upper_value = max_band_value
        
        # If the taxable income is not greater than the upper limit of the bracket
        # Then only the fraction of the bracket earned is paid
        else:
            amount_paid_at_this_bracket = (taxable_income - previous_bracket_upper_value) * rate
            fed_tax_owed += amount_paid_at_this_bracket
            break
    
    # Sum up tax credits
    sum_tax_credits = 0.00
    for k in tax_credits:
        sum_tax_credits += tax_credits[k]
    

    # Apply tax credits to get final federal tax owed
    fed_tax_owed = fed_tax_owed - sum_tax_credits

    return fed_tax_owed


# Read the file containing tax bracket info and store values in orderedDict
def get_file_info(filename):
    '''
    Inputs: 
    - filename : name of the file to be read in

    Output:
    - tax_brackets = OrderDict of taxable brackets (key is upper limit in each bracket, value is tax rate)
    '''

    # Open the file to read tax bracket info
    # The file has to be stuctured so that each line is:
    # upper value on tax bracket, tax rate
    # where the file is structured so that the lowest tax bracket is at the top and highest at bottom
    tax_bracket_file = open(filename, 'r')

    # Return dictionary is an ordered dict so we can iterate over keys deterministically
    tax_brackets = OrderedDict()

    while True:
        # Read line from file
        line = tax_bracket_file.readline()

        # Exit condition if file is done
        if not line:
            break

        # Split line on commas
        line_tokens = line.split(',')

        # Get values
        upper_tax_bracket_value = line_tokens[0]
        tax_bracket_rate = float(line_tokens[1])

        tax_brackets[upper_tax_bracket_value] = tax_bracket_rate
    
    return tax_brackets


# Helper function to get standard deduction corresponding to user filing status choice
def getStandardDeduction(filing_status, standard_deductions):
    '''
    Inputs:
    - filing_status: A number between 1 and 4 corresponding to filing status
    - standard_deductions: An OrderedDict containing standard deduction values for each of the filing types

    Output:
    - standard_deduction: The standard deduction corresponding to the user's choice
    '''

    counter = 1
    for filing_type, deduction_amount in standard_deductions.items():
        if (counter == filing_status):
            return deduction_amount
        counter += 1

    return 


# Calculates state tax owed
def calculateStateTax(agi, state_tax_info):
    '''
    Input:
    - agi: Adjusted Gross Income (same calculation as for federal tax)
    - state_tax_info: OrderedDict with tax information for state taxes

    Output:
    - state_tax_owed: The amount of state tax owed
    '''

    state_taxable_income = agi - float(state_tax_info["Personal Exemption"])
    
    state_tax_owed = state_taxable_income * float(state_tax_info["Flat Tax Rate"])

    return state_tax_owed


# Takes in one comnad line argument: Total Income (Salary)
def main():
    # Get income from user
    print("Enter total income amount without commas (e.g. for 50,000.00, put 50000.00)")
    total_income = float(input("> "))

    # Get filing status choice from user
    print("Enter filing status from one of the following options (enter the number corresponding to the option)")
    print("    1  Single")
    print("    2  Married filing jointly")
    print("    3  Married filing separately")
    print("    4  Head of Household")
    filing_status = int(input("> "))

    # Get the necessary information from relevant CSVs
    tax_brackets = get_file_info("csv_files/tax_brackets.csv")
    atl_deductions = get_file_info("csv_files/atl_deductions.csv")
    itemized_deductions = get_file_info("csv_files/itemized_deductions.csv")
    tax_credits = get_file_info("csv_files/tax_credits.csv")
    standard_deductions = get_file_info("csv_files/standard_deductions.csv")
    fica_taxes = get_file_info("csv_files/fica_taxes.csv")
    medicare_surtax_limits = get_file_info("csv_files/medicare_surtax.csv")
    state_tax_info = get_file_info("csv_files/state_tax_info.csv")

    # Get the standard deduction corresponding to the user's choice of filing status
    standard_deduction = getStandardDeduction(filing_status, standard_deductions)
    
    # Calclulate adjusted gross income
    agi = calculateAGI(total_income, atl_deductions)
    
    # Calculate taxable income 
    taxable_income = calculateTaxableIncome(agi, standard_deduction, itemized_deductions)
    
    # Calculate federal tax owed
    fed_tax_owed = calculateFederalTaxOwed(taxable_income, tax_brackets, tax_credits)

    # Calculate the amount of FICA tax (Social Security + Medicare) owed to the federal government
    fica_tax_owed = calculateFICAAmountsOwed(total_income, filing_status, fica_taxes, medicare_surtax_limits)

    # Total amount owed the federal government (federal tax and FICA)
    amount_owed_federal_gov = fed_tax_owed + fica_tax_owed

    # Calculate the amount of state tax owed
    amount_owed_state = calculateStateTax(agi, state_tax_info)

    # Total tax owed
    total_tax_owed = amount_owed_federal_gov + amount_owed_state

    # After tax pay
    after_tax_pay = total_income - total_tax_owed

    print()
    print(f"Total Federal Tax Owed: {round(amount_owed_federal_gov,2)}")
    print(f"Total State Tax Owed: {round(amount_owed_state,2)}")
    print(f"Total Tax Owed: {round(total_tax_owed,2)}")
    print()
    print(f"Take Home Pay: {round(after_tax_pay,2)}")
    return

    



# Force entry to main
if (__name__ == "__main__"):
    main()
