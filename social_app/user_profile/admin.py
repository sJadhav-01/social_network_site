from django.contrib import admin
from .models import AppUser, UserPost, PostComment, PostLike

# Register your models here.

admin.site.register(AppUser)
admin.site.register(UserPost)
admin.site.register(PostComment)
admin.site.register(PostLike)
