#test the calculations.py file
import pytest

import sys
from pathlib import Path

# Add the project root to Python path so we can import 'app'
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.calculations import add, subtract, multiply, divide, BankAccount, InsufficientFunds

@pytest.mark.parametrize("num1, num2, expected", [
    (3,2,5), (7,1,8), (12, 4, 16)
])
def test_add(num1, num2, expected):
    #the naming of those functions matter, if it does not start with testxxx, then it will be not auto-discovered.
    assert add(num1, num2) == expected
    # assert add(1, 2) == 3
    # assert add(-1, 1) == 0
    # assert add(-1, -1) == -2
    # assert add(0, 0) == 0
    # assert add(0, 1) == 1
    # assert add(0, -1) == -1
    # assert add(0, 0) == 0
    # assert add(0, 1) == 1
    # assert add(0, -1) == -1

def test_subtract():
    assert subtract(1, 2) == -1
    assert subtract(-1, 1) == -2
    assert subtract(-1, -1) == 0
    assert subtract(0, 0) == 0
    assert subtract(0, 1) == -1
    assert subtract(0, -1) == 1
    assert subtract(0, 0) == 0
    assert subtract(0, 1) == -1
    assert subtract(0, -1) == 1

def test_multiply():
    assert multiply(1, 2) == 2
    assert multiply(-1, 1) == -1
    assert multiply(-1, -1) == 1
    assert multiply(0, 0) == 0
    assert multiply(0, 1) == 0
    assert multiply(0, -1) == 0
    assert multiply(0, 0) == 0
    assert multiply(0, 1) == 0
    assert multiply(0, -1) == 0

def test_divide():
    assert divide(1, 2) == 0.5
    assert divide(-1, 1) == -1
    assert divide(-1, -1) == 1
    assert divide(0, 0) == 0
    assert divide(0, 1) == 0
    assert divide(0, -1) == 0
    assert divide(1, 0) == 0
    assert divide(-1, 0) == 0
    assert divide(-1, 0) == 0
    assert divide(0, 0) == 0
    assert divide(0, 1) == 0
    assert divide(0, -1) == 0
    assert divide(1, 0) == 0
    assert divide(-1, 0) == 0
    assert divide(-1, 0) == 0
    assert divide(0, 0) == 0
    assert divide(0, 1) == 0
    assert divide(0, -1) == 0

#create a fixture
@pytest.fixture
def zero_bank_account():
    return BankAccount()

@pytest.fixture
def bank_account():
    return BankAccount(50)

def test_bank_set_initial_amount(bank_account):
    # bank_account = BankAccount(50)
    assert bank_account.balance == 50


def test_bank_default_amount(zero_bank_account):
    # bank_account = BankAccount()
    # assert bank_account.balance == 0
    assert zero_bank_account.balance == 0


def test_withdraw(bank_account):
    # bank_account = BankAccount(50)
    bank_account.withdraw(20)
    assert bank_account.balance == 30

def test_deposit(bank_account):
    # bank_account = BankAccount(50)
    bank_account.deposit(30)
    assert bank_account.balance == 80

def test_collect_interest(bank_account):
    # bank_account = BankAccount(50)
    bank_account.collect_interest()
    assert bank_account.balance == 50 * 1.1

@pytest.mark.parametrize("deposited, withdrew, expected", [
    (200,100,100), 
    (50,10,40), 
    # (10, 50, -40)
])
def test_bank_transaction(zero_bank_account, deposited, withdrew, expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == expected

def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficientFunds):
        bank_account.withdraw(200)




