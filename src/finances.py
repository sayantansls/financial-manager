"""
author : sayantan (sayantan.ghosh@strandls.com)
"""

import json, os, sys, enum
from datetime import datetime
from pprint import pprint

json_file = '../data/financial-details.json'
prop_file = '../data/user-details.prop'
current_datetime = datetime.now()

def read_json(json_file):
	if not os.path.exists(json_file):
		raise Exception('Financial Details JSON file - {} not present'.format(json_file))
	return json.load(open(json_file, 'r'))

def read_properties(prop_file):
	prop_dict = dict()
	if not os.path.exists(prop_file):
		raise Exception('User Details file - {} not present'.format(prop_file))
	for line in open(prop_file, 'r').readlines():
		key, value = line.split('=')
		prop_dict[key] = value.strip()
	return prop_dict

def get_datetime_object(dateTimeStr):
	return datetime.strptime(dateTimeStr, '%d-%m-%Y %H:%M:%S.%f')

def get_investment_tenure(startDateObj, endDateObj):
	if current_datetime > endDateObj:
		time_diff = endDateObj - startDateObj
	elif current_datetime < endDateObj:
		time_diff = current_datetime - startDateObj
	return time_diff.days / 365

class InvestmentType(enum.Enum):
	fixedDeposit = 'Fixed Deposit'
	recurringDeposit = 'Recurring Deposit'
	ppf = 'Public Provident Fund'

class Investment():
	def __init__(self, principal, rate, time, startDate, endDate):
		self.principal = principal
		self.rate = rate
		self.time = time
		self.startDate = startDate
		self.endDate = endDate

	def toString(self):
		print('PRINCIPAL : {}, RATE : {}, TIME : {}, START DATE : {}, END DATE : {}'.format(self.principal, self.rate, \
			self.time, self.startDate, self.endDate))

class FixedDeposit(Investment):
	def __init__(self, principal, rate, time, startDate, endDate):
		super().__init__(principal, rate, time, startDate, endDate)
		self.type = InvestmentType.fixedDeposit.value

	def calculateAmount(self):
		startDateObj, endDateObj = [get_datetime_object(self.startDate), get_datetime_object(self.endDate)]
		time_diff_years = get_investment_tenure(startDateObj, endDateObj)
		# Interest is compounded quaterly for a fixed deposit
		amount = self.principal * (1 + (self.rate / 4) / 100) ** (4 * time_diff_years)
		return amount

class RecurringDeposit(Investment):
	def __init__(self, principal, rate, time, startDate, endDate):
		super().__init__(principal, rate, time, startDate, endDate)
		self.type = InvestmentType.recurringDeposit.value

	def calculateAmount(self):
		startDateObj, endDateObj = [get_datetime_object(self.startDate), get_datetime_object(self.endDate)]
		time_diff_years = int(get_investment_tenure(startDateObj, endDateObj))
		# Interest is compounded quaterly (amount is the sum of the series)
		tenure = round(time_diff_years) * 12
		maturity_amount = 0
		for month in range(tenure,0,-1):
			amount = self.principal * (1 + (self.rate / 4) / 100) ** (4 * (month/12))
			maturity_amount += amount
		return maturity_amount

class PublicProvidentFund(Investment):
	def __init__(self, principal, rate, time, startDate, endDate):
		super().__init__(principal, rate, time, startDate, endDate)
		self.type = InvestmentType.ppf.value

	def calculateAmount(self):
		pass

def print_user_details(user_details):
	for key in user_details.keys():
		print('{} : {}'.format(key.upper(), user_details[key]))

def create_investment_objects(investment_dict, investment_type):
	investment_objects = list()
	for investment in investment_dict[investment_type]:
		if investment_type == InvestmentType.fixedDeposit.value:
			deposit = FixedDeposit(investment['Principal'], investment['Rate'], investment['Time'], 
				investment['Start Date'], investment['End Date'])
		elif investment_type == InvestmentType.recurringDeposit.value:
			deposit = RecurringDeposit(investment['Principal'], investment['Rate'], investment['Time'],
				investment['Start Date'], investment['End Date'])
		else:
			raise Exception('Unknown Investment Type : {} provided'.format(investment_type))
		investment_objects.append(deposit)
	return investment_objects

def process_finance():
	user_details = read_properties(prop_file)
	print_user_details(user_details)
	financial_details = read_json(json_file)
	fd_objects = create_investment_objects(financial_details, InvestmentType.fixedDeposit.value)
	rd_objects = create_investment_objects(financial_details, InvestmentType.recurringDeposit.value)
	for fd_object in fd_objects:
		print(fd_object.calculateAmount())
	for rd_object in rd_objects:
		print(rd_object.calculateAmount())

if __name__ == '__main__':
	process_finance()
