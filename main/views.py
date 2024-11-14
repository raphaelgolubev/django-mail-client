from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render

from main.models import Account


def index(request):
    accounts = Account.objects.all()  # Получаем все аккаунты из базы данных
    return render(request, "accounts.html", {"accounts": accounts})


def messages_page(request, account_id):
    account = Account.objects.get(id=account_id)
    return render(request, "messages.html", {"account": account})


async def add_account(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    imap_server = request.POST.get("imap_server")
    imap_port = request.POST.get("imap_port")

    account = await Account.objects.acreate(
        email=email, password=password, imap_server=imap_server, imap_port=imap_port
    )

    account_dict = model_to_dict(account)

    return JsonResponse({"status": "success", "account": account_dict})


async def delete_account(request):
    if request.method == "POST":
        account_id = request.POST.get("id")
        try:
            account = await Account.objects.aget(id=account_id)
            result = await account.adelete()  # Удаляем аккаунт
            return JsonResponse({"status": "success", "result": result})
        except Account.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Аккаунт не найден."})
    return JsonResponse({"status": "error", "message": "Неверный метод."})
