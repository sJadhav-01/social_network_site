from django import template

register = template.Library()

@register.filter(name='post_like_count')
def post_like_count(postlikecount, post):
    count=0
    if post:
        for postlikeobj in postlikecount:
            if post == postlikeobj.post:
                count += 1
    return count

