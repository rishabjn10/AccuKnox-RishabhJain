import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import UserProfile, FriendRequest
from .forms import UserProfileForm, FriendRequestForm
from .serializers import FriendRequestSerializer
from django.contrib.auth import authenticate, login
from django_ratelimit.decorators import ratelimit


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def create_user_profile(request):
    if request.method == "POST":
        try:
            error = False
            if request.body:
                requestBody = json.loads(request.body)
                requestBody["email"] = requestBody["email"].lower()
                form = UserProfileForm(requestBody)
                if len(UserProfile.objects.filter(email=requestBody["email"])) >= 1:
                    error = {'email': 'Email already exists'}
                if not error and form.is_valid():
                    user_profile = form.save(commit=False)
                    if requestBody['password'] == requestBody['confirm_password']:
                        user = User.objects.create_user(
                            username=user_profile.email,
                            first_name=user_profile.name.split()[0],
                            last_name=user_profile.name.split()[-1],
                            email=user_profile.email,
                            password=requestBody['password']
                        )
                    else:
                        error = {'Password': 'Passwords do not match'}
                        return JsonResponse({"success": False, "errors": error}, status=400)
                    user_profile.user = user
                    user_profile.save()
                    return JsonResponse({'success': True, 'message': 'User profile created successfully'})
                else:
                    if not error:
                        error = form.errors
                    return JsonResponse({"success": False, "errors": error}, status=400)
            else:
                error = {"Empty request": "No data in the request body"}
                return JsonResponse({"success": False, "errors": error}, status=400)
        except Exception as e:
            print(e)
            print("---------------------------------------------")
            return JsonResponse({"success": False, "errors": e}, status=400)

    elif request.method == "OPTIONS":
        response = HttpResponse()
        response["allow"] = ",".join(["POST", "OPTIONS"])
        return response


@require_http_methods(["POST", "OPTIONS"])
@login_required
@ratelimit(key='user', rate='3/m')
@csrf_exempt
def send_friend_request(request):
    if request.method == "POST":
        try:
            error = False
            if request.body:
                requestBody = json.loads(request.body)
                senderProfile = UserProfile.objects.get(
                    email=request.user.email)
                try:
                    receiverProfile = UserProfile.objects.get(
                        email=requestBody["action_to"])
                    if receiverProfile == senderProfile:
                        error = {
                            "Invalid friend request": "You cannot send friend request to yourself"}
                    form = FriendRequestForm(
                        {"sender": senderProfile, "receiver": receiverProfile})
                    if len(FriendRequest.objects.filter(sender=senderProfile, receiver=receiverProfile)) >= 1:
                        error = {
                            'Friend request': 'Friend request already sent'}
                except Exception as e:
                    error = {
                        'Invalid receiver': 'Invalid receiver details for the friend request.'}
                if not error and form.is_valid():
                    friend_request = form.save(commit=False)
                    friend_request.status = "pending"
                    friend_request.save()
                    return JsonResponse({'success': True, 'message': 'Friend request sent successfully'})
                else:
                    if not error:
                        error = form.errors
                    return JsonResponse({"success": False, "errors": error}, status=400)
            else:
                error = {"Empty request": "No data in the request body"}
                return JsonResponse({"success": False, "errors": error}, status=400)
        except Exception as e:
            print(e)
            print("---------------------------------------------")
            return JsonResponse({"success": False, "errors": e}, status=400)

    elif request.method == "OPTIONS":
        response = HttpResponse()
        response["allow"] = ",".join(["POST", "OPTIONS"])
        return response


@csrf_exempt
@login_required
@require_http_methods(["POST", "GET", "OPTIONS"])
def friend_request(request):
    if request.method == "POST":
        try:
            error = False
            if request.body:
                requestBody = json.loads(request.body)
                if not (requestBody["action"] == "accepted" or requestBody["action"] == "rejected"):
                    error = {
                        "Invalid action": "Invalid action on friend request."}
                receiverProfile = UserProfile.objects.get(
                    email=request.user.email)
                try:
                    senderProfile = UserProfile.objects.get(
                        email=request.GET.get("action_to"))
                    friend_request = FriendRequest.objects.get(
                        sender=senderProfile, receiver=receiverProfile)
                    if len(FriendRequest.objects.filter(sender=senderProfile, receiver=receiverProfile)) < 1:
                        error = {
                            'Friend request': 'No friend request between these users found'}
                    serializer = FriendRequestSerializer(
                        friend_request, data={"status": requestBody["action"]}, partial=True)
                except Exception as e:
                    error = {
                        'Invalid sender': 'Invalid sender details for the friend request.'}
                if not error and serializer.is_valid():
                    if requestBody["action"] == "accepted":
                        friend_request.accept()
                    elif requestBody["action"] == "rejected":
                        friend_request.reject()
                    return JsonResponse({'success': True, 'message': 'Friend request accepted/rejected successfully'})
                else:
                    if not error:
                        error = serializer.errors
                    return JsonResponse({"success": False, "errors": error}, status=400)
            else:
                error = {"Empty request": "No data in the request body"}
                return JsonResponse({"success": False, "errors": error}, status=400)
        except Exception as e:
            print(e)
            print("---------------------------------------------")
            return JsonResponse({"success": False, "errors": e}, status=400)
    if request.method == "GET":
        senderProfile = UserProfile.objects.get(
            email=request.GET.get("action_to"))
        receiverProfile = UserProfile.objects.get(
            email=request.user.email)
        friend_requests = FriendRequest.objects.filter(
            sender=senderProfile, receiver=receiverProfile)
        serialized_requests = [
            {'from': friends.sender.name, 'status': friends.status} for friends in friend_requests if friends.status == "pending"]
        return JsonResponse({"success": True, "friend_requests": serialized_requests}, status=200)

    elif request.method == "OPTIONS":
        response = HttpResponse()
        response["allow"] = ",".join(["POST", "GET", "OPTIONS"])
        return response


@csrf_exempt
@login_required
@require_http_methods(["GET", "OPTIONS"])
def friends(request):
    if request.method == "GET":
        userProfile = UserProfile.objects.get(
            email=request.user.email)
        friends = userProfile.friends.all()
        serialized_friends = [
            friend.email for friend in friends]
        return JsonResponse({"success": True, "friends": serialized_friends}, status=200)

    elif request.method == "OPTIONS":
        response = HttpResponse()
        response["allow"] = ",".join(["GET", "OPTIONS"])
        return response


@require_http_methods(["GET", "OPTIONS"])
@login_required
def search_users(request):
    if request.method == "GET":
        try:
            error = False
            params = request.GET
            search_by = params.get('search_by', '')
            page_number = params.get('page', 1)
            query = params.get('query', '')
            if params:
                if search_by == "name":
                    matching_users = UserProfile.objects.filter(
                        name__icontains=query).order_by('name')
                    paginator = Paginator(matching_users, 10)
                    try:
                        page = paginator.page(page_number)
                    except Exception as e:
                        return JsonResponse({"success": False, "errors": 'Invalid page number'}, status=400)
                    serialized_users = [
                        {'id': user.id, 'name': user.name} for user in page]

                    return JsonResponse({"success": True, "users": serialized_users, "total_pages": paginator.num_pages}, status=200)

                elif search_by == "email":
                    try:
                        matching_user = UserProfile.objects.get(
                        email=query.lower())
                    except Exception as e:
                        return JsonResponse({"success": False, "errors": 'This user does not exist'}, status=400)
                    serialized_user = {'id': matching_user.id, 'name': matching_user.name} 

                    return JsonResponse({"success": True, "user": serialized_user}, status=200)
                else:
                    error = {
                        "Invalid search by": "Invalid value in 'search_by' param"}
                    return JsonResponse({"success": False, "errors": error}, status=400)
            if not params:
                error = {
                    "Empty search request": "No params in the search request"}
                return JsonResponse({"success": False, "errors": error}, status=400)
        except Exception as e:
            print(e)
            print("---------------------------------------------")
            return JsonResponse({"success": False, "errors": e}, status=400)

    elif request.method == "OPTIONS":
        response = HttpResponse()
        response["allow"] = ",".join(["GET", "OPTIONS"])
        return response


@csrf_exempt
@require_http_methods(["POST"])
def user_login(request):
    requestBody = json.loads(request.body)
    username = requestBody['username'].lower()
    password = requestBody['password']

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse({'message': 'Login successful'})
    else:
        return JsonResponse({'message': 'Invalid credentials'}, status=401)
