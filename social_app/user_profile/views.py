from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from .models import AppUser, UserPost
from django.views import View
from django.core.exceptions import ValidationError
from datetime import datetime
# Create your views here.


class Home(View):
    def get(self, request):
        posts = UserPost.objects.all()[:5]
        data = {
            'posts' : posts     
        }
        return render(request, 'home.html', data)


class Signup(View):
    def get(self, request):
        """Render the signup form."""
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
                # request.session['user_email'] = user.email
                # request.session['user_first_name'] = user.first_name
                # request.session['user_last_name'] = user.last_name
                request.session['is_authenticated'] = True
                user_info = {
                    'first_name': user.first_name,
                    'last_name' : user.last_name,
                }

                return render(request, 'home.html', {'user' : user_info})
            else: 
                error_message = 'Password entered is not correct !!'
                return render(request, 'login.html', {'error' : error_message})
        return render(request, 'login.html')
    

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
        return redirect ('home')


class Profile(View):
    
    def get(self, request):
        return render(request, 'profile.html')
    
    def post(self, request):
        post_content = request.POST.get('post')
        user_id = request.session.get('user')
        user=AppUser.objects.get(id= user_id)
        user_info = {   'id' : user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
        print(post_content)
        print(user)
        if user and post_content:
            userpost = UserPost.objects.create(user=user, post=post_content)
        return redirect('profile')