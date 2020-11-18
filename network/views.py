from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from django.core.paginator import Paginator

from .models import User, posts, likes, followers


def index(request):
    form = ""
    sk = posts.objects.all().order_by('-id')
    lk=set()
    for dk in sk:
        lk.add(User.objects.get(id=f"{dk.User_id}"))
    paginator = Paginator(sk, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    lik=None
    if request.user.is_authenticated:
        lik = likes.objects.filter(User_id=request.user.id)
    if request.user.is_authenticated:
        #form = PostForm()
        if request.method == 'POST':
            if request.POST.get('content') == "":
                return render(request, "network/index.html",{
    "posts":page_obj,
    "names":lk,
    "likes":lik,
    "Error":"Please add something to post."
})
            else:
                #formx = PostForm(request.POST,request.FILES)
                posts(User_id=request.user.id,content=request.POST.get('content'),post_image=request.FILES.get('post_image'),likes=0).save()
                return HttpResponseRedirect('/')
    
    return render(request, "network/index.html",{
        "posts":page_obj,
        "names":lk,
        "likes":lik,
        "form":form
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            print(request.FILES.get('user_image'))
            user = User(username=username, email=email, password=password,user_image=request.FILES.get('user_image'))
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request,id):
    if request.method=="GET":
        data = User.objects.get(id=id)
        fkx = True
        if not followers.objects.filter(User_id=id,follower_id=request.user.id):
            fkx = False
        else:
            fkx = True

        post = posts.objects.filter(User_id=id).order_by('-id')
        paginator = Paginator(post, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number) 
        following = followers.objects.filter(follower_id=id)
        followingx = len(following)
        follow = followers.objects.filter(User_id=id)
        followx = len(follow)
        lik=None
        if request.user.is_authenticated:
            lik = likes.objects.filter(User_id=request.user.id)
        return render(request, "network/profile.html",{
            "posts":page_obj,
            "userx": data,
            "name": data.username,
            "following": followingx,
            "followers": followx,
            "image":data.user_image,
            "id": int(id),
            "fkx":fkx,
            "likes":lik,
        })
    elif request.method=='POST':
        data = User.objects.get(id=request.user.id)
        url = reverse('profile', kwargs={'id': request.user.id})
        if request.POST.get('content'):
            data.user_description = request.POST.get('content')
        else:
             data.user_image = request.FILES.get('user_image2')
            
        data.save()
        return HttpResponseRedirect(url)
        


@login_required
def follow(request):
    if request.method=='POST':
        data = json.loads(request.body)
        if data.get('content')=='Follow':
            if not followers.objects.filter(User_id=data.get('id'),follower_id=request.user.id):
                sk=followers(User_id=data.get('id'),follower_id=request.user.id)
                sk.save()
                return JsonResponse({
                    "message": "following this User."
                }, status=201)

            else:
                return JsonResponse({
                    "message": "Already following."
                }, status=201)

        elif data.get('content') == 'Unfollow':
            if not followers.objects.filter(User_id=data.get('id'),follower_id=request.user.id):
                return JsonResponse({
                    "message": "Already Unfollowed"
                }, status=201)

            else:
                sk = followers.objects.filter(User_id=data.get('id'),follower_id=request.user.id)
                sk.delete()
                return JsonResponse({
                    "message": "You have unfollowed this user"
                }, status=201)

        else:
            return JsonResponse({
                    "message": "Please dont change the button value."
                }, status=400)

    else:
        return JsonResponse({
                        "message": "wrong request method"
                    }, status=400)


@login_required
def following(request):
    folk = followers.objects.filter(follower_id=request.user.id).order_by('-id')
    jk=[]
    for nk in folk:
        jk.append(nk.User_id)

    sk = posts.objects.filter(User_id__in=jk).order_by('-id')
    paginator = Paginator(sk, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    
    lk=set()
    for dk in sk:
        lk.add(User.objects.get(id=f"{dk.User_id}"))

    lik=None
    if request.user.is_authenticated:
        lik = likes.objects.filter(User_id=request.user.id)
    
    return render(request, "network/following.html",{
        "posts":page_obj,
        "names":lk,
        "likes":lik
    })

@login_required
def edit(request):
    if request.method=='POST':
        #data = json.loads(request.body)
        try:
            print(request.POST.get("post_id"))
            nk = posts.objects.get(id=request.POST.get("post_id"))
            if request.user.id == nk.User_id:
                nk.content = request.POST.get("content")
                if(request.FILES.get('post_image2')):
                    nk.post_image = request.FILES.get('post_image2')
                nk.save()
                return JsonResponse({
                        "message": "Post edited"
                    }, status=201)
            else:
                return JsonResponse({
                        "message": "Can't edit the Post"
                    }, status=400)
        except ObjectDoesNotExist:
            return JsonResponse({
                        "message": "Can't edit the Post"
                    }, status=400)
    else:
        return JsonResponse({
                        "message": "wrong request method"
                    }, status=400)
    



@login_required
def likesx(request):
    if request.method=='POST':
        data = json.loads(request.body)
        if data.get('content') == "Like":
            nk = likes.objects.filter(post_id=data.get('id'),User_id=request.user.id)
            if not nk:
                likes(post_id=data.get('id'),User_id=request.user.id).save()
                vk = posts.objects.get(id=data.get('id'))
                vk.likes = vk.likes + 1
                vk.save()
                return JsonResponse({
                    "message": "Post Liked",
                    "likes": posts.objects.get(id=data.get('id')).likes
                }, status=201)
            else:
                return JsonResponse({
                    "message": "Post already Liked"
                }, status=400)

        elif data.get('content') == "Unlike":
            nk = likes.objects.filter(post_id=data.get('id'),User_id=request.user.id)
            if not nk:
                return JsonResponse({
                    "message": "Post already unliked."
                }, status=400)
            else:
                nk.delete()
                vk = posts.objects.get(id=data.get('id'))
                vk.likes = vk.likes - 1
                vk.save()
                return JsonResponse({
                    "message": "Post Unliked",
                    "likes": posts.objects.get(id=data.get('id')).likes
                }, status=201)

        else:
            return JsonResponse({
                    "message": "There is some error"
                }, status=400)

    else:
        return JsonResponse({
                        "message": "wrong request method"
                    }, status=400)


@login_required
def follower(request,id):
    if request.method=='POST':
        print(request.user.id+int(id))
        if request.user.id==int(id):
            sk = followers.objects.filter(follower_id=request.user.id).order_by('-id')
            lk=[]
            for dk in sk:
                lk.append(User.objects.get(id=f"{dk.User_id}"))
            paginator = Paginator(lk, 10) 
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, "network/followers.html",{
                        "posts":page_obj,
                        "title": "Following"
                    })

    else:
        return HttpResponseRedirect("/")


@login_required
def following2(request,id):
    if request.method=='POST':
        if request.user.id==int(id):
            sk = followers.objects.filter(User_id=request.user.id).order_by('-id')
            lk=[]
            for dk in sk:
                lk.append(User.objects.get(id=f"{dk.follower_id}"))
            paginator = Paginator(lk, 10) 
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, "network/followers.html",{
                        "posts":page_obj,
                        "title":"Followers"
                    })

    else:
        return HttpResponseRedirect("/")
    
        

    













    

        


