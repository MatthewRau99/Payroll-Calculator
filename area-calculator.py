import pandas as pd
from datetime import datetime
import os

# Variables that should change

# Input the filename for the area info
county = pd.read_csv("Sample-Employee-Input.csv")
# The names of all the employees in the area
countyEmployees = ['Employee1', 'Employee2', 'Employee3', 'Employee4', 'Employee5', 'Employee6',
                  'Employee7', 'Employee8', 'Employee9']
countyEmployeeCount = len(countyEmployees)

# Start dates for week 1 and week 2 of the pay period
week1StartDate = datetime(day=29, month=4, year=2023)
week2StartDate = datetime(day=6, month=5, year=2023)

# Probably won't need to change these unless something huge happens
countyManager = 'Employee4'
owners = ['Employee9', 'Employee5']
ceo = 'Employee5'

# Don't change anything below this line 
# ---------------------------------------------------------


# Extract the Hours info on each employee
employeeInfo = pd.DataFrame(county.Employees[0:countyEmployeeCount+1])
employeeInfo['Week1Hours'] = county['Hours Worked Week 1'][0:countyEmployeeCount+1]
employeeInfo['Week2Hours'] = county['Hours Worked Week 2'][0:countyEmployeeCount+1]



# Extract each job into a dataframe
payPeriod = county.loc[1]['Unnamed: 1']
payPeriodDashed = payPeriod.replace('/', '-')
os.mkdir(f'county-{payPeriodDashed}')

firstCol = county['Pay Tracker']
startIndex = firstCol[firstCol == 'First Name'].index[0]
headers = county.loc[startIndex]
jobs = county[startIndex + 1:]
jobs.columns = [headers]



# Create dataframe with each payment going to an employee
payments = pd.DataFrame(columns=['Employee','First Name', 'Last Name', 'Date', 'Serviced Revenue','Upsold Revenue', None, 
                    'Service Team Members', 'Team Commission Percent', 'Your Commission Percent', 'Service Payout Amount',
                    None, 'Sales Commission Percent', 'Sales Payout Amount', None, 'Upsell Type (screens, extra windows, etc',
                    'Upsell Commission Percent', 'Upsell Payout Amount', None,
                    'Manager Commission Percent', 'Manager Payout Amount', None,
                    'CEO Commission Percent', 'CEO Payout Amount', None,
                    'Owner Commission Percent', 'Owner Payout Amount'])

for index, row in jobs.iterrows():
    if pd.isnull(row['Service Team']):
        continue
    workers = [x.strip() for x in row['Service Team'].split(',')]
    fullPercent = 0.2
    servicePercent = fullPercent / len(workers)
    serviceCommission = round(float(row['Serviced Amount'].replace('$', '')) * servicePercent, 2)
    if type(row['Upseller']) != float:
        upsellers = [x.strip() for x in row['Upseller'].split(',')]
        fullUpsellPercent = 0.2
        upsellPercent = fullUpsellPercent / len(upsellers)
        upsellCommission = round(float(row['Upsold Amount (If Applicable)']) * upsellPercent,2)
    else:
        upsellers = []
        upsellPercent = None
        upsellCommission = None

    salesman = row['Sales Rep']
    salesPercent = 0.2
    salesCommission = round(float(row['Serviced Amount'].replace('$', '')) * salesPercent, 2)

    managerPercent = 0.1
    managerCommission = round((float(row['Serviced Amount'].replace('$', '')) + float(row['Upsold Amount (If Applicable)'])) * managerPercent, 2)

    ceoPercent = 0.05
    ceoCommission = round((float(row['Serviced Amount'].replace('$', '')) + float(row['Upsold Amount (If Applicable)'])) * ceoPercent, 2)

    ownerPercent = 0.1
    ownerCommission = round((float(row['Serviced Amount'].replace('$', '')) + float(row['Upsold Amount (If Applicable)'])) * ownerPercent, 2)

    employees = workers.copy()
    if salesman not in employees:
        employees.append(salesman)
    
    if countyManager not in employees:
        employees.append(countyManager)

    for owner in owners:
        if owner not in employees:
            employees.append(owner)

    for employee in employees:
        payments.loc[len(payments.index)] = [
            employee, row['First Name'], row['Last Name'], row['Date'],
            row['Serviced Amount'].replace('$', ''), row['Upsold Amount (If Applicable)'], None, ','.join(workers),
            fullPercent if employee in workers else None, servicePercent if employee in workers else None, 
            serviceCommission if employee in workers else None, None,
            salesPercent if employee == salesman else None, salesCommission if employee == salesman else None, None,
            row['Upsold Services Rendered (If Applicable)'] if employee in upsellers else None,
            upsellPercent if employee in upsellers else None, upsellCommission if employee in upsellers else None, None,
            managerPercent, managerCommission, None, ceoPercent, ceoCommission, None, ownerPercent, ownerCommission
        ]



# Build the personal report for each employee and save
for employee in countyEmployees:
    df = payments[payments.Employee == employee]
    df = df.drop(labels='Employee', axis=1).reset_index()
    df = df.drop(labels='index', axis=1)
    df.index = range(9, 9+len(df))

    totalService = sum(df['Service Payout Amount'].dropna())
    totalSales = sum(df['Sales Payout Amount'].dropna())
    totalUpsell = sum(df['Upsell Payout Amount'].dropna())

    if employee == countyManager:
        totalManager = sum(df['Manager Payout Amount'].dropna())
    else:
        totalManager = 0

    if employee == ceo:
        totalCeo = sum(df['CEO Payout Amount'].dropna())
    else:
        totalCeo = 0
    
    if employee in owners:
        totalOwner = sum(df['Owner Payout Amount'].dropna())
    else:
        totalOwner = 0
    
    totalCompensation = round(totalService + totalSales + totalUpsell + totalManager + totalCeo + totalOwner, 2)
    
    totalHours = float(employeeInfo[employeeInfo.Employees == employee].Week1Hours) + float(employeeInfo[employeeInfo.Employees == employee].Week2Hours) 

    NoneArray = [None] * 24
    finalFile = pd.DataFrame(columns=['First Name', 'Last Name', 'Date', 'Serviced Revenue','Upsold Revenue', None, 
                    'Service Team Members', 'Team Commission Percent', 'Your Commission Percent', 'Service Payout Amount',
                    None, 'Sales Commission Percent', 'Sales Payout Amount', None, 'Upsell Type (screens, extra windows, etc',
                    'Upsell Commission Percent', 'Upsell Payout Amount', None,
                    'Manager Commission Percent', 'Manager Payout Amount', None,
                    'CEO Commission Percent', 'CEO Payout Amount', None,
                    'Owner Commission Percent', 'Owner Payout Amount'])
    finalFile.loc[len(finalFile.index)] = ['Employee', employee] + NoneArray
    finalFile.loc[len(finalFile.index)] = ['Pay Period', payPeriod] + NoneArray
    finalFile.loc[len(finalFile.index)] = ['Total Compensation', totalCompensation] + NoneArray
    finalFile.loc[len(finalFile.index)] = ['Total Hours Worked', totalHours] + NoneArray
    finalFile.loc[len(finalFile.index)] = ['Average Hourly Rate', round(totalCompensation / totalHours, 2)] + NoneArray
    for i in range(3):
        finalFile.loc[len(finalFile.index)] = [None, None] + NoneArray

    finalFile.loc[len(finalFile.index)] = ['Customer', None, None, None, None, None, 'Service Commissions', None, None, None, None, 'Sales Commissions', None, None, 'Upsell Commissions', None, None, None, 'Manager Commissions', None, None, 'CEO Commissions', None, None, 'Owner Commissions', None]

    finalFile.loc[len(finalFile.index)] = list(df.columns)

    for index, row in df.iterrows():
        finalFile.loc[len(finalFile.index)] = list(row)

    if employee not in owners:
        finalFile = finalFile.drop(labels=['Owner Commission Percent', 'Owner Payout Amount'], axis=1)

    if employee != ceo:
        finalFile = finalFile.drop(labels=['CEO Commission Percent', 'CEO Payout Amount'], axis=1)

    if employee != countyManager:
        finalFile = finalFile.drop(labels=['Manager Commission Percent', 'Manager Payout Amount'], axis=1)

    finalFile.to_csv(f'county-{payPeriodDashed}/{employee}-{payPeriodDashed}-county.csv', header=False)   



# Build dataframe with row for each employee and their info
fullPayroll = pd.DataFrame(columns=['Employee1', 'Pay1', 'Hours1', 'AvgPay1', None, 'Pay2', 'Hours2', 'AvgPay2', None, 'Employee2', 'TotalCompensation'])

for employee in countyEmployees:
    df = payments[payments.Employee == employee].reset_index()
    df = df.drop(labels='index', axis=1)
    df['dateTime'] = df.Date.apply(lambda x : datetime(day=int(x.split('/')[1]), month=int(x.split('/')[0]), year=int(x.split('/')[2])))
    week1 = df[df.dateTime < week2StartDate]
    week2 = df[df.dateTime >= week2StartDate]

    week1Hours = float(employeeInfo[employeeInfo.Employees == employee].Week1Hours) 
    week2Hours = float(employeeInfo[employeeInfo.Employees == employee].Week2Hours) 

    week1Service = sum(week1['Service Payout Amount'].dropna())
    week1Sales = sum(week1['Sales Payout Amount'].dropna())
    week1Upsell = sum(week1['Upsell Payout Amount'].dropna())
    if employee == countyManager:
        week1Manager = sum(week1['Manager Payout Amount'].dropna())
    else:
        week1Manager = 0
    week1Compensation = round(week1Service + week1Sales + week1Upsell + week1Manager, 2)
    week2Service = sum(week2['Service Payout Amount'].dropna())
    week2Sales = sum(week2['Sales Payout Amount'].dropna())
    week2Upsell = sum(week2['Upsell Payout Amount'].dropna())
    if employee == countyManager:
        week2Manager = sum(week2['Manager Payout Amount'].dropna())
    else:
        week2Manager = 0
    week2Compensation = round(week2Service + week2Sales + week2Upsell + week2Manager, 2)
    
    totalCompensation = week1Compensation + week2Compensation

    fullPayroll.loc[len(fullPayroll.index)] = [
        employee, week1Compensation, week1Hours, round(week1Compensation/week1Hours, 2) if week1Hours != 0 else 0, None,
        week2Compensation, week2Hours, round(week2Compensation/week2Hours, 2) if week2Hours != 0 else 0, None,
        employee, totalCompensation
    ]




# Build the report and save
payrollFile = pd.DataFrame(columns=(['Employee Payroll'] + [None]*10))
payrollFile.loc[len(payrollFile.index)] = ['Pay Period:', payPeriod] + [None]*9
payrollFile.loc[len(payrollFile.index)] = [None]*11
payrollFile.loc[len(payrollFile.index)] = ['Week 1', None, None, None, None, 'Week 2', None, None, None, 'Total Compensation by Employee', None]
payrollFile.loc[len(payrollFile.index)] = [None]*11
payrollFile.loc[len(payrollFile.index)] = ['Employee', 'Pay', 'Hours worked', 'Average Pay/Hr', None, 'Pay', 'Hours worked', 'Average Pay/Hr', None, 'Employee', 'Total Compensation']

for index, row in fullPayroll.iterrows():
    payrollFile.loc[len(payrollFile.index)] = list(row)
    
payrollFile.to_csv(f'county-{payPeriodDashed}/county-Payroll-{payPeriodDashed}.csv')