from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.context_processors import request
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.six import b
from notifications.signals import notify
from app.models import CustomUser
import re
from .models import *
from django.shortcuts import *
from django.contrib.auth.models import User
# Create your views here.
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect


IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg','gif','bmp']
@login_required
def upload_text(request):
    if request.method =='POST':
        text = request.POST['text-text']
        share = request.POST['share_to']

        text_broadcast = TextBroadcast()
        text_broadcast.user = request.user
        text_broadcast.message = text

        if share == 'followers':
            text_broadcast.send_to_all=False
        else:
            text_broadcast.send_to_all=True

        text_broadcast.save()

        return redirect('broadcast:index')

    else:
        raise Http404

@login_required
def upload_image(request):
    if request.method == 'POST':
        image = request.FILES['image-image']
        desc = request.POST['text-image']
        share = request.POST['share_to']

        image_broadcast = ImageBroadcast()
        image_broadcast.image = image
        image_broadcast.user = request.user
        image_broadcast.description = desc

        if share == 'followers':
            image_broadcast.send_to_all=False
        else:
            image_broadcast.send_to_all=True


        image_broadcast.save()

        return redirect('broadcast:index')

    else:
        raise Http404

# @login_required
# def upload_ride(request):
#     if request.method == 'POST':
#         source = request.POST['source']
#         destination = request.POST['destination']
#         date = request.POST['date']
#         share = request.POST['share_to']

#         ride_broadcast = RideBroadcast()
#         ride_broadcast.user = request.user
#         ride_broadcast.date_needed = date
#         ride_broadcast.source = source
#         ride_broadcast.dest = destination

#         if share == 'followers':
#             ride_broadcast.send_to_all=False
#         else:
#             ride_broadcast.send_to_all=True

#         ride_broadcast.save()

#         return redirect('broadcast:index')

#     else:
#         raise Http404

@login_required
def upload_direction(request):
    if request.method == 'POST':
        source = request.POST['ride-source']
        dest = request.POST['ride-destination']
        add_info = request.POST['ride-text']
        share = request.POST['share_to']

        direct_broadcast = DirectionBroadcast()
        direct_broadcast.user = request.user
        direct_broadcast.location = source
        direct_broadcast.destination = dest
        direct_broadcast.additional_info = add_info
        if share == 'followers':
            direct_broadcast.send_to_all=False
        else:
            direct_broadcast.send_to_all=True

        direct_broadcast.save()

        return redirect('broadcast:index')

    else:
        raise Http404


def index(request,
    template='broadcast/broadcasts_home.html',
    page_template='broadcast/broadcast_template.html'):
    user_info = {}
    trends = get_trending_hasgtags()
    broadcasts = Broadcast.objects.order_by('pk').reverse().select_subclasses()
    user_info['mentions'] = TextBroadcast.objects.filter(Q(message__icontains='@'+str(request.user)) ).order_by("-message")
    user_info['mention_count'] = user_info['mentions'].count()
    try:
        users = CustomUser.objects.order_by('?').exclude(followee__follower=request.user).exclude(pk=request.user.id)
    except:
        users = None

    context ={ 'broadcasts':broadcasts,
    'trends': trends,
    'user_info': user_info,
    'page_template': page_template,
    'users':users,

    }

    if request.is_ajax():
        template = page_template
    return render_to_response( template, context, context_instance=RequestContext(request))

@login_required
def like_broadcast(request,broadcast_id):
    broadcast = get_object_or_404(Broadcast,pk=broadcast_id)
    test = Like.objects.filter(liker=request.user,broadcast_message=broadcast)
    if(test.exists()):
        test.delete()

    else:
        like = Like()
        like.broadcast_message = broadcast
        like.liker = request.user

        like.save()

        notify.send(request.user,recipient=broadcast.user,verb='Liked Broadcast ',action_object=broadcast,
                    description=str(request.user)+' Liked your Broadcast',level='info')


#@@@@@@@@@@@@@@@@
@login_required
def mention_broadcast(request,broadcast_id):
    broadcast = get_object_or_404(Broadcast,pk=broadcast_id)
    test = Like.objects.filter(mentionor=request.user,broadcast_m=broadcast)
    if(test.exists()):
        test.delete()

    else:
        mention = Like()
        mention.broadcast_m = broadcast
        mention.mention = request.user

        mention.save()

        notify.send(request.user,recipient=broadcast.user,verb='mentioned Broadcast ',action_object=broadcast,
                    description=str(request.user)+' mentioned your Broadcast',level='info')





    page_template='broadcast/broadcast_template.html'
    template = page_template
    broadcasts = Broadcast.objects.order_by('pk').reverse().select_subclasses()

    context ={ 'broadcasts':broadcasts,
               'page_template': page_template
               }
    return render_to_response( template, context, context_instance=RequestContext(request))



@login_required
def rebc(request,bc_id):


    broadcast = Broadcast.objects.filter(pk=bc_id).select_subclasses()[0]
    broadcast.pk = None
    broadcast.id = None
    broadcast.bc_from = broadcast.user
    broadcast.user = request.user
    broadcast.bc_time = timezone.now()
    broadcast.bc_date = timezone.now()
    broadcast.save()

    notify.send(request.user,recipient=broadcast.bc_from,verb='Re-Bc\'d Broadcast ',action_object=broadcast,
                description=str(request.user)+' Shared your Broadcast',level='info')

    return redirect('broadcast:index')


def broadcast_view(request,bc_id):
    broad  = Broadcast.objects.filter(pk=bc_id).select_subclasses()[0]

    return render(request,'broadcast/broadcast_view.html',{'broad':broad})


@login_required
def comment(request,broadcast_id):
    broadcast = get_object_or_404(Broadcast,pk=broadcast_id)
    comment = Comment()
    comment.commenter = request.user
    comment.broadcast_message = broadcast
    try:
        comment.comment = request.POST['comment']
    except:
        redirect(broadcast.get_absolute_url())

    comm = Comment.objects.filter(broadcast_message=broadcast).values_list('commenter',flat=True).distinct()
    #to add distinct on commenters when using mysql finally



    if comm.count() >= 1:

        for user in comm:

            recipient = CustomUser.objects.get(pk=user)
            if recipient == request.user:
                pass
            elif recipient == broadcast.user:
                pass
            else:
                notify.send(request.user,recipient=recipient,verb='commented on Broadcast ',action_object=broadcast,
                      description=str(request.user)+' commented on a Broadcast You are following ',level='info')


    notify.send(request.user,recipient=broadcast.user,verb='commented on Broadcast ',action_object=broadcast,
                    description=str(request.user)+' commented on your broadcast ',level='info')


    comment.save()

    return redirect('broadcast:view', broadcast_id)


def get_trending_hasgtags():
    trends = {}
    broadcast = TextBroadcast.objects.all()
    for broadcast_data in broadcast:
        text = broadcast_data.message
        pat = re.compile(r'[#](\w+)')
        hashtags = pat.finditer(text)
        for hasgtag in hashtags:
            try:
                trends[hasgtag.group().lower()]+=1
            except KeyError:
                trends[hasgtag.group().lower()] = 1
    trending = []
    for w in sorted(trends, key=trends.get, reverse=True):

        trending.append(dict(hasgtag=w, broadcast_count=trends[w]))
    return trending[:3]


@login_required
def do_follow(request,followee,follower):

    foll = CustomUser.objects.get(pk=follower)   #followed user
    fole = CustomUser.objects.get(pk=followee)   #who to follow

    check = Follow.objects.filter(follower=foll,followee=fole)
    if not check.exists():
        f = Follow(follower=foll,followee=fole)
        f.save()

        notify.send(foll, recipient=fole, verb='Follow', level='info', action_object=f,description=str(foll.username)+' followed you')

    else:

        check.delete()

    return redirect('app:profile',followee)

@login_required
def all_ride_requests(request):
    user = get_object_or_404(CustomUser,pk=request.user.id)
    requests = Request.objects.filter(ride__user=user).order_by('pk')
    context ={
        'requests':requests,

    }

    return render(request,'app/request/all_requests.html',context)

@login_required
def preferences(request):

    return render(request,'app/dashboard/preferences.html')

@login_required
def messages(request):
    messages = Message.objects.filter(recipient=request.user,deleted=False).order_by('date').reverse()
    context = {
        'messages':messages,
    }
    return render(request,'app/dashboard/dashboard_messages.html',context)



def search(request):
    trends = get_trending_hasgtags()
    query = request.GET.get('search')
    if str(query) is '':
        return HttpResponseRedirect('/')
    pat = re.compile(r'[@](\w+)')
    attags = pat.finditer(query)
    search_profile = None
    for attag in attags:
        try:
            search_profile = User.objects.get(username = attag.group()[1:])
            return HttpResponseRedirect('/accounts/profile/user/%s'%search_profile.username)
        except ObjectDoesNotExist:
            search_profile = None
        break
    
    search_data = TextBroadcast.objects.filter(message__icontains=query).order_by('-message')
    search_dataa = ImageBroadcast.objects.filter(description__icontains=query).order_by('-description')
    people = CustomUser.objects.filter(Q(username__icontains=query) | Q(full_name__icontains=query) | Q(short_name__icontains=query))
    return render(request, 'broadcast/search_results.html', {'search_data':search_data, 'search_dataa':search_dataa, 'query':query, 'search_profile':search_profile, 'people':people, 'trends':trends})
    #We can differenitate here on the basis of the search query we have got like @ and # or any other textual query







def markdown_find_mentions(markdown_text):
    """
    To find the users that mentioned
    on markdown content using `BeautifulShoup`.

    input  : `markdown_text` or markdown content.
    return : `list` of usernames.
    """
    mark = markdownify(markdown_text)
    soup = BeautifulSoup(mark, 'html.parser')
    return list(set(
        username.text[1::] for username in
        soup.findAll('a', {'class': 'direct-mention-link'})
    ))









