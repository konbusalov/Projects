from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm, RegisterForm
from .utils.decorators import role_required
from .models import Bank, Account, Loan, Lease, Transaction
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from decimal import Decimal

def index(request):
    return render(request, 'index.html')

@role_required('CLIENT')
def client_dashboard(request):
    accounts = Account.objects.filter(user=request.user)
    loans = Loan.objects.filter(user=request.user)
    leases = Lease.objects.filter(user=request.user)
    return render(request, 'client_dashboard.html', {"accounts": accounts, "loans": loans, "leases": leases})

@role_required('OPERATOR', 'MANAGER')
def staff_dashboard(request):
    transactions = Transaction.objects.all()
    if request.user.role == 'OPERATOR':
        return render(request, 'operator_dashboard.html', {"transactions": transactions})
    if request.user.role == 'MANAGER':
        loans = Loan.objects.all()
        leases = Lease.objects.all()
        return render(request, 'manager_dashboard.html', {"transactions": transactions,
                                                          "loans": loans,
                                                          "leases": leases })
    
@role_required('ADMIN')
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@role_required('SPECIALIST')
def specialist_dashboard(request):
    return render(request, 'specialist_dashboard.html')




def sign_in(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('posts')

        form = LoginForm()
        return render(request, 'login.html', {'form':form})
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}, welcome back!')
                return redirect('/')
            
        messages.error(request,f'Invalid username or password')
        return render(request, 'login.html', {'form': form})
    
def sign_out(request):
    logout(request)
    messages.success(request,f'You have been logged out.')
    return redirect('/login')      

    

def sign_up(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'You have signed up successfully.')
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'register.html', {'form': form})
        
@role_required('CLIENT')       
def create_account(request):
    initialize()
    if request.method == "POST":
        bank_name = request.POST.get("bank")
        bank = Bank.objects.get(name=bank_name)
        user = request.user
        account = Account(bank=bank, user=user)
        account.save() 
        return HttpResponseRedirect('/client_dashboard/')
    banks = Bank.objects.all()
    return render(request, 'create_account.html', {"banks": banks})

@role_required('CLIENT')
def make_deposit(request, account_number):
    try:
        account = Account.objects.get(account_number=account_number)

        if request.method == "POST":
            amount = request.POST.get('amount')
            account.balance += Decimal(amount)
            account.save()
            return HttpResponseRedirect('/client_dashboard/')
        else:
            return render(request, 'make_deposit.html')
    except Account.DoesNotExist:
        return HttpResponseNotFound("<h2>Product not found</h2>")
    
@role_required('CLIENT')
def make_transfer(request, account_number):
    try:
        account = Account.objects.get(account_number=account_number)

        if request.method == "POST":
            amount = request.POST.get('amount')
            to_account = request.POST.get('to_account')
            recieve_account = Account.objects.get(account_number=to_account)
            account.balance -= Decimal(amount)
            recieve_account.balance += Decimal(amount)
            Transaction.objects.create(user=request.user, account=account, to_account=recieve_account, amount=amount)
            account.save()
            recieve_account.save()
            return HttpResponseRedirect('/client_dashboard/')
        else:
            return render(request, 'make_transfer.html')
    except Account.DoesNotExist:
        return HttpResponseNotFound("<h2>Product not found</h2>")
    
@role_required('CLIENT')
def make_loan(request):
    if request.method == "POST":
        try:
            user = request.user
            account_number = request.POST.get("account_number")
            amount = Decimal(request.POST.get("amount"))
            term = int(request.POST.get("term"))
            account = Account.objects.get(account_number=account_number)
            Loan.objects.create(user=user, account=account, amount=amount, months=term)
            return render(request, 'loan_submitted.html')
        except (ValueError, TypeError):
            return HttpResponse("Invalid input data", status=400)
    return redirect('client_dashboard')

@role_required('CLIENT')
def make_lease(request):
    if request.method == "POST":
        try:
            user = request.user
            account_number = request.POST.get("account_number")
            amount = Decimal(request.POST.get("amount"))
            term = int(request.POST.get("term"))
            account = Account.objects.get(account_number=account_number)
            Lease.objects.create(user=user, account=account, amount=amount, months=term)
            return render(request, 'lease_submitted.html')
        except (ValueError, TypeError):
            return HttpResponse("Invalid input data", status=400)
    return redirect('client_dashboard')

@role_required('OPERATOR', 'MANAGER')
def cancel_transaction(request, id):
    try:
        transaction = Transaction.objects.get(id=id)
        account = transaction.account
        to_account = transaction.to_account
        amount = transaction.amount
        account.balance += Decimal(amount)
        account.save()
        to_account.balance -= Decimal(amount)
        to_account.save()
        transaction.delete()
        return redirect('staff dashboard')
    except Transaction.DoesNotExist:
        return HttpResponseNotFound("<h2>Product not found</h2>")
    
@role_required('MANAGER')
def approve_loan(request, id):
    try:
        loan = Loan.objects.get(id=id)
        loan.approve(request.user)
        account = loan.account
        account.balance += loan.amount
        account.save()
        return redirect('staff dashboard')
    except Loan.DoesNotExist:
        return HttpResponseNotFound("<h2>Product not found</h2>")
    
@role_required('MANAGER')
def reject_loan(request, id):
    try:
        loan = Loan.objects.get(id=id)
        loan.reject(request.user)
        return redirect('staff dashboard')
    except Loan.DoesNotExist:
        return HttpResponseNotFound("<h2>Product not found</h2>")
    
@role_required('MANAGER')
def approve_lease(request, id):
    try:
        lease = Lease.objects.get(id=id)
        lease.approve(request.user)
        account = lease.account
        account.balance += lease.amount
        account.save()
        return redirect('staff dashboard')
    except lease.DoesNotExist:
        return HttpResponseNotFound("<h2>Product not found</h2>")
    
@role_required('MANAGER')
def reject_lease(request, id):
    try:
        lease = Lease.objects.get(id=id)
        lease.reject(request.user)
        return redirect('staff dashboard')
    except lease.DoesNotExist:
        return HttpResponseNotFound("<h2>Product not found</h2>")








    

def initialize():
    if Bank.objects.all().count() == 0:
        Bank.objects.create(name = "Alpha-Bank")
        Bank.objects.create(name = "BelarusBank")
        Bank.objects.create(name = "PriorBank")

