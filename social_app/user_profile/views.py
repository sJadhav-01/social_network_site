from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from .models import AppUser, UserPost, PostLike, FriendRequest, Friends
from django.views import View
from django.core.exceptions import ValidationError
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Count
import json

# Create your views here.


class Home(View):
    def get(self, request):
        user_id = request.session.get('user')
        if user_id:
            try:
                user = AppUser.objects.get(id=user_id)
                posts = UserPost.objects.all().order_by('-id').annotate(like_count=Count('likes'))
                liked_post_ids = PostLike.objects.filter(user=user).values_list('post_id', flat=True)
                return render(request, 'home.html', {'user': user, 'posts': posts, 'liked_post_ids': liked_post_ids})
            except AppUser.DoesNotExist:
                return redirect('login')
        return redirect('login')


class Signup(View):
    def get(self, request):
        return render(request, 'signup.html')
    
    def post(self, request):
        """Handle form submission, validation, and user creation."""
        post_data = request.POST

        # Retrieve form data
        first_name = post_data.get('first_name')
        last_name = post_data.get('last_name')
        gender = post_data.get('gender')
        dob = post_data.get('dob')
        phone = post_data.get('phone')
        email = post_data.get('email')
        password = post_data.get('password')

        # Dictionary to retain values in case of error
        values = {
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'dob': dob,
            'phone': phone,
            'email': email,
        }

        # Perform manual validation
        error_message = self.validateUser(
            first_name, last_name, gender, dob, phone, email, password
        )

        if not error_message:
            # Hash the password for security
            hashed_password = make_password(password)

            # Convert dob string to a date object
            try:
                birthday_date = datetime.strptime(dob, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                error_message = 'Invalid date format.'
                return render(request, 'signup.html', {
                    'error': error_message,
                    'values': values
                })

            # Create and save the new user
            user = AppUser(
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                birthday=birthday_date,
                phone=phone,
                email=email,
                password=hashed_password
            )
            try:
                user.full_clean()  # Use Django's built-in model validation
                user.save()
            except ValidationError as e:
                return render(request, 'signup.html', {
                    'error': e.messages[0],
                    'values': values
                })

            # Redirect after successful signup (Post/Redirect/Get pattern)
            return redirect('login') 
        else:
            # Re-render the form with error message and previous values
            return render(request, 'signup.html', {
                'error': error_message,
                'values': values
            })

    def validateUser(self, first_name, last_name, gender, dob, phone, email, password):
        """Performs custom validation checks."""
        if not first_name or len(first_name) < 3:
            return 'First name must be at least 3 characters.'
        if not last_name or len(last_name) < 3:
            return 'Last name must be at least 3 characters.'
        if not gender:
            return "Gender is not mentioned"
        if not dob:
            return 'Date of birth not mentioned'
        if not phone or len(phone) < 10:
            return 'Phone number must be at least 10 digits.'
        if not email:
            return 'Email is required.'
        if not password or len(password) < 6:
            return 'Password must be at least 6 characters.'
        if AppUser.objects.filter(email=email).exists():
            return 'Email is already registered.'
        return None
    



class Login(View):

    def get(self, request):
        if request.session.get('user'):
            return redirect('home')
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = AppUser.objects.get(email = email)
        error_message = None
        if user:
            flag = check_password(password, user.password)
            if flag:
                request.session['user'] = user.id
                request.session['user_email'] = user.email
                request.session['user_first_name'] = user.first_name
                request.session['user_last_name'] = user.last_name
                request.session['is_authenticated'] = True
                return redirect('home')
            else: 
                error_message = 'Password entered is not correct !!'
                return render(request, 'login.html', {'error' : error_message})
        return redirect('login')
    

# class LoginView(View):
#     def get(self, request):
#         """Renders the login form."""
#         return render(request, 'login.html')

#     def post(self, request):
#         """Authenticates and logs in a user, then stores user data in the session."""
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         user = authenticate(request, username=email, password=password)

#         if user is not None:
#             login(request, user)
            
#             # Logic to store user info in the session
#             request.session['user_id'] = user.id
#             request.session['user_email'] = user.email
#             request.session['user_first_name'] = user.first_name
#             request.session['is_authenticated'] = True

#             # Redirect to the home page or a success page.
#             return redirect('home')  
#         else:
#             messages.error(request, 'Invalid email or password. Please try again.')
#             return render(request, 'login.html')

class Logout(View):
    def get(self, request):
        request.session.clear()
        return redirect ('login')


class Profile(View):
    
    def get(self, request):
        user_id = request.session.get('user')
        if not user_id:
            return redirect('login')
        try:
            user = AppUser.objects.get(id=user_id)
            posts = UserPost.objects.filter(user_id = user_id).order_by('-id').annotate(like_count=(Count('likes')))  # here 'likes' is a relateed_name
            liked_post_ids = PostLike.objects.filter(user=user).values_list('post_id', flat=True)
            return render(request, 'profile.html', {'user': user, 'posts': posts, 'liked_post_ids': liked_post_ids})
        except AppUser.DoesNotExist:
            return redirect('login')
       
    
    def post(self, request):
        post_content = request.POST.get('post')
        user_id = request.session.get('user')
        if not user_id:
            return redirect('login') 
        try: 
            user=AppUser.objects.get(id=user_id)
            if post_content:
                UserPost.objects.create(user=user, post_content=post_content)
            return redirect('profile')
        except AppUser.DoesNotExist:
            return redirect('login')


class OtherUserProfile(View):
    def get(self, request):
        other_user_id = request.session.get('otheruser')
        print(other_user_id)
        user_id = request.session.get('user')
        print(user_id)
        if not other_user_id:
            return redirect('home')
        try:
            user = AppUser.objects.get(id=user_id)
            print(user)
            other_user = AppUser.objects.get(id=other_user_id)
            print(other_user)
            posts = UserPost.objects.filter(user_id=other_user_id).order_by('-id').annotate(like_count=(Count('likes')))
            liked_post_ids = PostLike.objects.filter(user=user).values_list('post_id', flat=True)
            request_sent = FriendRequest.objects.filter(user=user, other_user=other_user).exists()
            return render (request, 'otheruserprofile.html', {'otheruser' : other_user, 'posts': posts, 'liked_post_ids': liked_post_ids, 'request_sent': request_sent})
        except AppUser.DoesNotExist:
            return redirect('home')
        

    def post(self, request):
        other_user_id = request.POST.get('otheruser')
        print(other_user_id)
        if other_user_id:
            request.session['otheruser'] = other_user_id
            try:
                if AppUser.objects.filter(id=other_user_id).exists():
                    return redirect('otheruserprofile')
            except AppUser.DoesNotExist:
                return redirect('home')
       

class FriendsList(View):

    def get(self, request):
        user_id = request.session.get('user')
        if not user_id:
            return redirect('login')
        
        user = AppUser.objects.get(id=user_id)
   
        received_reqs = FriendRequest.objects.filter(other_user=user)
        received_req_ids = FriendRequest.objects.filter(other_user=user).values_list('user__id', flat=True)
        requests_sent_to = FriendRequest.objects.filter(user=user).values_list('other_user', flat=True)
        friends = Friends.objects.filter(user=user)
        friends_id = Friends.objects.filter(user=user).values_list('friend', flat=True)
        random_users = AppUser.objects.exclude(id=user_id).order_by('?')[:10]
        # random_users = AppUser.objects.exclude(id=user.id).exclude(id__in=requests_sent_to).order_by('?')[:10]
        return render(request, 'friends.html', {'friends': friends, 'received_reqs': received_reqs, 'friend_suggs': random_users, 'requests_sent_to': requests_sent_to, 'received_req_ids':received_req_ids , 'friends_id': friends_id })


# api view
# @method_decorator(csrf_exempt, name='dispatch')
class PostLikeCheck(View):
    def post(self, request, post_id):
        # csrf_token = request.COOKIES['csrf_token']
        # print(csrf_token)
        user_id = request.session.get('user')
        # print(user_id)
        user = AppUser.objects.get(id=user_id)
        if not user:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        # user = request.user # Get the authenticated user
        try:
            post = UserPost.objects.get(id=post_id)
        except UserPost.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        
        if PostLike.objects.filter(post=post, user=user).exists():
             # Check if the user has already liked the post
            PostLike.objects.filter(post=post, user=user).delete()
            status = 'unliked'
        else:
            PostLike.objects.create(user=user, post=post)
            status = 'liked'
       
        # Note: # this is to remember. instead of accessing full object only one column of table can be accessed PostLike.post
             
        post_like_count = PostLike.objects.filter(post=post).count()
        return JsonResponse({
            'status': status,
            'likes': post_like_count
        })
    

class FriendRequestCheck(View):

    def post(self, request, other_user_id):
        user_id = request.session.get('user')
        if not user_id: 
            return JsonResponse({'error': 'Authentication required'}, status=401)
        try:
            user = AppUser.objects.get(id=user_id)
            other_user = AppUser.objects.get(id=other_user_id)
        except AppUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        if FriendRequest.objects.filter(user=user, other_user=other_user).exists():
            FriendRequest.objects.filter(user=user, other_user=other_user).delete()
            request_status = 'request_not_sent'
        else:
            FriendRequest.objects.create(user=user, other_user=other_user)
            request_status = 'request_sent'
        
        return JsonResponse({
            'request_status': request_status
        })

      

class FriendRequestAction(View):
    
    def post(self, request, received_req_id):
        # Get action from JSON body
        try:
            data = json.loads(request.body)
            action = data.get('action')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Authenticate the user
        user_id = request.session.get('user')
        if not user_id:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            user = AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Process the friend request
        try:
            received_request = FriendRequest.objects.get(id=received_req_id)
        except FriendRequest.DoesNotExist:
            return JsonResponse({'error': 'Friend request not found'}, status=404)

        # Verify the current user is the recipient of the request
        if received_request.other_user != user:
            return JsonResponse({'error': 'Unauthorized action'}, status=403)
        
        request_status = 'rejected' # Default status

        # 4. Perform the action
        if action == 'accept':
            # Create a new Friends relationship
            Friends.objects.create(user=user, friend=received_request.user)
            Friends.objects.create(user=received_request.user, friend=user)
            
            # Delete the friend request
            received_request.delete()
            request_status = 'accepted'
        
        elif action == "reject":
            # Just delete the friend request
            received_request.delete()
        
        return JsonResponse({
            'request_status': request_status
        })