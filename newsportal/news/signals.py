from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import PostCategory
from .tasks import send_email
import re


@receiver(m2m_changed, sender=PostCategory)
def new_post_email(instance, **kwargs):
    if kwargs['action'] == 'post_add':
        regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]"
                           r"+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]"
                           r"+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
        for new_post_category in instance.category.all():
            for user_to_email in new_post_category.subscribers.all():
                if re.fullmatch(regex, user_to_email.email):
                    print(user_to_email.email)
                    send_email.apply_async(
                        (user_to_email.username, new_post_category.category_name,
                         instance.title, instance.text, instance.pk,
                         user_to_email.email),
                        countdown=5,
                    )
