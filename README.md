# Income Tax Calculator 

This repo will calculate the amount of federal and state tax owed. You just will need to update some tax information (for the relevant) tax year for it to be usable. Other than updating the CSV files containing that information, all you need is your total income (salary) and this script will calcualte your taxes owed and take-home pay for you.

## Usage 

The script `tax_calc.py` will handle all calculations. You can run the file in a bash terminal with `python3 tax_calc.py`. 

When the script runs it will ask you to input your total income and then will ask you if you how you will file (e.g. single, married). When entering your income be sure to ommit commas or dollar signs. For example, if I want to enter $50,000, I would enter 50000 when prompted. Similarly, when entering your filing status, you will be presented with 4 options, each of which labeled with a number 1 through 4. Enter your selection as the number (e.g. 1).

## CSV Files

The CSV files folder contains the following list of `.csv` files, which are read by the Python script to do the calculations. The script makes some assumptions about the format of each file. So, those assumptions will be clarified below each file name
- `atl_deductions.csv`
    - This file contains your ["Above the Line Deductions"](https://www.investopedia.com/terms/a/above-the-line-deduction.asp) with one deduction per line. Each line must be in following format: `name,deduction amount`. See the file for the format example.
- `fica_taxes.csv`
    - This file contains information regarding [FICA taxes (Social Security and Medicare)](https://www.irs.gov/taxtopics/tc751).  This file must contain three lines, with each line of the form `FICA Tax Name,rate` where rate is a decimal. There should be three lines in the file:
        - Social Security
        - Medicare Tax
        - Medicare Surtax
- `itemized_deductions.csv`
    - This file should contain all of your itemized deductions. The program will sum all of your itemized deductions and compare it to the standard deductions to determine which one you should use (and will take the higher deduction for you automatically). 
    - Each line of the file should be of the form `deduction name,deduction amount`. See the file for the example format.
- `max_ss_tax_income_limit.csv`
    - This file gives the [wage base limit](https://www.irs.gov/taxtopics/tc751) for the social security FICA tax. It should just be one line with the number corresponding to the limit 
        - (do not include commas in the number  - e.g. $50,000 would be 50000).
- `medicare_surtax.csv`
    - This file contains the minimum salary values for which the Medicare Surtax FICA tax begins to be applied. There are two values for this threshold: Single and Jointly. See [this IRS site](https://www.irs.gov/taxtopics/tc751) to get the necessary values. 
- `standard_deductions.csv`
    - This file contains the dollar amounts for each standard deduction option. There should be four options:
        - Single
        - Married filing jointly
        - Married filing separately
        - Head of Household
    - NOTE: The order of these values within the `.csv` file matters. Do not change the order of these lines within the file. You can change the key values if you want, but do not change the order of the lines. The reason for this, is the data is read into an OrderedDict and the `i`-th entry corresponds to the `i`-th numeric option for filing status. 
- `state_tax_info.csv`
    - This file contains information for state tax. It is currently configured for Michigan, which has a personal exemption and flat tax rate. There is a single function `calculateStateTax()` which handles the calculation of the state tax, so change the calculations there as necessary.
- `tax_brackets.csv`
    - This file contains the information for each federal tax bracket. It is configured so that each line of the file is formatted as: `upper limit of bracket, bracket tax rate`. 
    - So, for example, if the first income tax bracket is $0 - $9,875 at 10% tax rate, then the line would read: `9874.00,0.1`
    - NOTE: The order of the lines matter.  The `.csv` data is read into an OrderedDict which is then processed under the assumption that the file was structured so that the first line corresponded to the lowest tax bracket and the last line corresponded to the highest tax bracket.
    - NOTE: The final tax bracket is listed as having an upper value of $1 million currently for ease of notation. If you make more than $1 million than good for you and this will still work regardless.  
- `tax_credits.csv`
    - This file contains all of your tax credits
    - Structure the file similarly to how `itemized_deductions.csv` is structured with each line of the file containing one tax credit name and value (e.g. `tax credit name, tax credit value in dollars`)


## Debugging

The following are some "gatcha's" that could cause issues:
- All numbers in the CSV should be entered without dollar signs or commas
    - e.g. The number $50,000.00 should be entered in any of the csv files as 50000.00
- The following files require that the order of the lines relative to one another remain unchanged:
    - `tax_brackets.csv`
    - `standard_deductions.csv`
- Do not remove `.csv` files from the folder and into the root directory. The script assumes that all the `.csv` files are in the `csv_files/` folder.

