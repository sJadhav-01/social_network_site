from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class AppUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    # Redefine the username field to be the email for a more modern approach.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    # New fields
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    birthday = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True)
    
    # You can customize built-in fields like this, but be careful.
    # The AbstractUser email field is already unique, so this is just for clarity.
    email = models.EmailField(unique=True, blank=False, null=False)


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='appuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='appuser_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    # Methods for a Custom User Model are not necessary for basic functionality.
    # isEmailExists method is redundant because of unique=True on the email field.
    # The __str__ method should return a unique identifier, like the username or email.
    def __str__(self):
        return self.email
    

class UserPost(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    post = models.TextField()

    def __str__(self):
        return f'Post by {self.user.email}'

class PostComment(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f'Comment by {self.user.email} on {self.post}'


class PostLike(models.Model):
    # This model simply represents a like. A user likes a post.
    # To get the total number of likes, you count the objects.
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
    
    # To prevent a user from liking a post multiple times, add a unique constraint.
    class Meta:
        unique_together = ('user', 'post')
        
    def __str__(self):
        return f'{self.user.email} likes {self.post}'