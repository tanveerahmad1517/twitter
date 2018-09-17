from django.db import models
from django.conf import *
from django.utils import timezone
from model_utils.managers import InheritanceManager
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import cloudinary
from cloudinary.models import CloudinaryField
import re
# from django.contrib.auth.models import User

class Broadcast(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='%(app_label)s_%(class)s_related')
    date = models.DateField(_('broadcast date'),default=timezone.now)
    time = models.TimeField(_('time'),default=timezone.now)
    send_to_all = models.BooleanField(_('send to all'),default=False)
    bc_from = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,default=None, null=True,on_delete=models.CASCADE, related_name='bcfrom')
    bc_time = models.TimeField(_('rebc time'),default=timezone.now)
    bc_date = models.DateField(_('rebc date'),default=timezone.now)
    
    objects = InheritanceManager()

    
    # def save(self, *args, **kwargs):
    #     super(Broadcast, self).save(*args, **kwargs)
    #     mentions = self.get_mentions()
    #     if mentions:
    #         verb = "mentioned you"
    #         new_notification(
    #             origin_user = self.user.username,
    #             affected_users = mentions,
    #             verb=verb,
    #             target=self,
    #             )

    def children(self):
        return Broadcast.objects.filter(parent=self).order_by("-timestamp")

    @property
    def is_parent(self):
        if self.parent == None:
            return True
        return False

    @property
    def reply_count(self):
        return Broadcast.objects.filter(parent=self).count()

    # def get_mentions(self):
    #     text = self.message
    #     pattern = re.compile(r'[@](\w+)')
    #     mentions = pattern.finditer(text)
    #     mention_list = []
    #     for mention in mentions:
    #         username = mention.group()[1:]

    #     return mefntion_list

    def html_tags_edit(self):
        text = self.message
        description = self.description
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['alt', 'src'],
        }
        try:
            final_text = ""
            pat = re.compile(r'[#,@](\w+)')
            hashtags = pat.finditer(text)
            i=0
            for hasgtag in hashtags:
                search_query = "\'" + "/search?search=" + urllib.quote(hasgtag.group()) + "\'"
                final_text += (text[i:hasgtag.span()[0]] + "<a href=" + search_query + ">" + hasgtag.group() + "</a>")
                i = hasgtag.span()[1]
            final_text += (text[i:])
            if final_text == "":
                text = bleach.clean(text, tags=['img', 'a'], attributes=attrs, strip=True)
                text = bleach.linkify(text)
                return mark_safe(text)
            else:
                final_text = bleach.clean(final_text, tags=['img', 'a'], attributes=attrs, strip=True)
                final_text = bleach.linkify(final_text)
                return mark_safe(final_text)
        except:
            return text



    def liked(self):
        num = Like.objects.filter(broadcast_message=self).values_list('liker')

        result = []
        for liker in num:
            print(liker)
            user = liker[0]
            result.append(user)

        return result
    def mentioned(self):
        num = Mentioned.objects.filter(broadcast_message=self).values_list('mentionor')

        result = []
        for mentionor in num:
            print(mentionor)
            user = mentionor[0]
            result.append(user)

        return result

    def get_absolute_url(self):
        return '/broadcast/%d/view/' % self.pk

    def html_tags_edit(self):
        text = self.message
        description = self.description
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['alt', 'src'],
        }
        try:
            final_text = ""
            pat = re.compile(r'[#,@](\w+)')
            hashtags = pat.finditer(text)
            i=0
            for hasgtag in hashtags:
                search_query = "\'" + "/search?search=" + urllib.quote(hasgtag.group()) + "\'"
                final_text += (text[i:hasgtag.span()[0]] + "<a href=" + search_query + ">" + hasgtag.group() + "</a>")
                i = hasgtag.span()[1]
            final_text += (text[i:])
            if final_text == "":
                text = bleach.clean(text, tags=['img', 'a'], attributes=attrs, strip=True)
                text = bleach.linkify(text)
                return mark_safe(text)
            else:
                final_text = bleach.clean(final_text, tags=['img', 'a'], attributes=attrs, strip=True)
                final_text = bleach.linkify(final_text)
                return mark_safe(final_text)
        except:
            return text


class TextBroadcast(Broadcast):
    message = models.TextField()
    class Meta:
       ordering = ['message']


class ImageBroadcast(Broadcast):
    image = CloudinaryField('image', blank=True, null=True) 
    description = models.TextField()
    class Meta:
       ordering = ['description']

@receiver(pre_delete, sender=ImageBroadcast)
def profile_delete(sender, instance, **kwargs):
    cloudinary.uploader.destroy(instance.image.public_id)    


# class RideBroadcast(Broadcast):
#     source = models.CharField(_('source'),max_length=256)
#     dest = models.CharField(_('destination'),max_length=256)
#     date_needed = models.DateField(_('date needed'),default=timezone.now)


class DirectionBroadcast(Broadcast):
    location = models.TextField(_('current Location'))
    destination = models.TextField(_('destination'))
    additional_info = models.TextField(_('additional information'))



class Comment(models.Model):

    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='commenter')
    broadcast_message = models.ForeignKey(Broadcast,on_delete=models.CASCADE,related_name='broadcast_comment')
    comment = models.TextField(_('comment'),blank=False)
    date = models.DateField(_('date'),default=timezone.now)
    time = models.TimeField(_('time'),default=timezone.now)




class Like(models.Model):
    liker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='liker')
    broadcast_message = models.ForeignKey(Broadcast, on_delete=models.CASCADE,related_name='broadcast_like')
    date = models.DateField(_('date'), default=timezone.now)
    time = models.TimeField(_('time'), default=timezone.now)



class Mentioned(models.Model):
    mentionor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='mentionor')
    broadcast_m = models.ForeignKey(Broadcast, on_delete=models.CASCADE,related_name='broadcast_mention')
    date = models.DateField(_('date'), default=timezone.now)
    time = models.TimeField(_('time'), default=timezone.now)




















