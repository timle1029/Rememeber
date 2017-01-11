import datetime

from django.core.files import File
from django.core.files.base import ContentFile
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.shortcuts import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.core.files import File  # you need this somewhere
import urllib.request
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.template.loader import render_to_string
from django.utils import timezone

from django.http import HttpResponse, Http404
from mimetypes import guess_type
import json
from PIL import Image, ImageDraw, ImageFont
import time

from django.utils.html import strip_tags

from core.models import *
from core.forms import *


def sign_in(request):
    if request.user.is_authenticated():
        return redirect('/rememeber/home')
    context = {}
    return render(request, 'core/sign_in.html', context)


@login_required
def home(request):
    context = {}
    user = request.user
    meme_list = MemeObject.objects.all().order_by('-created_at')
    context['user'] = user
    context['user_id'] = user.id
    context['meme_list'] = meme_list
    return render(request, 'core/MainStream.html', context)


@login_required
@transaction.atomic
def new_meme(request, thread_id=None, user_id=None):
    context = {}
    user = request.user
    first_name = user.first_name
    last_name = user.last_name
    context['curr_user_full_name'] = first_name + ' ' + last_name
    background_library_all = list(MemeBackground.objects.filter(created_by=request.user))
    background_library = []
    path_library = []
    for bg in background_library_all:
        path = bg.image.url
        if path not in path_library:
            background_library.append(bg)
            path_library.append(path)
    if request.method == 'GET':
        form = NewMemeForm()
        if thread_id is not None:
            form.fields['thread_id'].initial = thread_id
        if user_id is not None:
            form.fields['reply_user_id'].initial = user_id
        context['form'] = form
        context['user'] = request.user
        context['meme_bg_lib'] = background_library
    return render(request, 'core/editting.html', context)


@login_required
@transaction.atomic
def create_meme(request, meme_bg_id=None):
    context = {}
    if request.method == 'POST':
        if meme_bg_id is None:
            form = NewMemeForm(request.POST, request.FILES)
        else:
            chosen_bg = MemeBackground.objects.get(pk=meme_bg_id)
            form = NewMemeForm(request.POST, initial={'background': chosen_bg})
        if form.is_valid():
            user = request.user
            if meme_bg_id is not None:
                background_model = MemeBackground.objects.get(pk=meme_bg_id)
                form.cleaned_data['background'] = background_model.image
            new_background = MemeBackground(created_by=user, image=form.cleaned_data['background'])
            new_background.save()
            new_title = form.cleaned_data['title']
            top_caption = form.cleaned_data['top_caption']
            bottom_caption = form.cleaned_data['bottom_caption']
            thread_id = form.cleaned_data['thread_id']
            reply_user_id = form.cleaned_data['reply_user_id']
            tag = form.cleaned_data['tag']
            text_color = form.cleaned_data['text_color']

            temp_caption_list = [top_caption, bottom_caption]
            encoded_captions = json.dumps(temp_caption_list)
            if text_color == "blue":
                color = (0, 0, 255)
            elif text_color == 'red':
                color = (255, 0, 0)
            elif text_color == 'white':
                color = (255, 255, 255)
            else:
                color = (255, 255, 255)
            img = Image.open(form.cleaned_data['background'])
            img_size_width = img.size[0]
            img_size_height = img.size[1]
            draw = ImageDraw.Draw(img)
            font_path = 'core/static/core/font/arial.ttf'

            # portion of image width you want text width to be
            img_width_fraction = 0.6
            img_height_fraction = 0.20
            font_size_top = 10  # starting font size
            font_top = ImageFont.truetype(font_path, font_size_top)
            while font_top.getsize(temp_caption_list[0])[0] < img_width_fraction * img_size_width and \
                            font_top.getsize(temp_caption_list[0])[1] < img_height_fraction * img_size_height:
                font_size_top += 10
                font_top = ImageFont.truetype(font_path, font_size_top)
            final_t_capt_size = font_top.getsize(temp_caption_list[0])
            final_t_capt_width = final_t_capt_size[0]
            top_top_pos = int(0.1 * img_size_height)
            top_left_pos = int((img_size_width - final_t_capt_width) / 2.0)

            font_size_bottom = 10
            font_bottom = ImageFont.truetype(font_path, font_size_bottom)
            while font_bottom.getsize(temp_caption_list[1])[0] < img_width_fraction * img_size_width and \
                            font_bottom.getsize(temp_caption_list[1])[1] < img_height_fraction * img_size_height:
                font_size_bottom += 10
                font_bottom = ImageFont.truetype(font_path, font_size_bottom)
            final_b_capt_size = font_bottom.getsize(temp_caption_list[1])
            final_b_capt_width = final_b_capt_size[0]
            final_b_capt_height = final_b_capt_size[1]
            bottom_top_pos = int(img_size_height - final_b_capt_height - 0.1 * img_size_height)
            bottom_left_pos = int((img_size_width - final_b_capt_width) / 2.0)

            caption_positions = [(top_left_pos, top_top_pos), (bottom_left_pos, bottom_top_pos)]
            encoded_positions = json.dumps(caption_positions)
            draw.text(caption_positions[0], temp_caption_list[0], font=font_top, fill=text_color)
            draw.text(caption_positions[1], temp_caption_list[1], font=font_bottom, fill=text_color)
            time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
            file_name = user.username + '_' + time_stamp + '.jpg'
            file_path_prefix = 'media/temp/'
            file_path_prefix_short = 'temp/'
            file_path = file_path_prefix + file_name
            short_file_path = file_path_prefix_short + file_name
            img.save(file_path)
            new_meme = MemeObject(owner=user, title=new_title, captions=encoded_captions,
                                  caption_positions=encoded_positions,
                                  background=new_background, image=short_file_path,
                                  popularity_score=0, tags=tag)

            new_meme.save()
            if thread_id.__len__() != 0:
                thread_meme = get_object_or_404(MemeObject, pk=thread_id)
                memeWar = get_object_or_404(MemeWar, thread_meme=thread_meme)
                memeWar.meme_list.add(new_meme)
                if not memeWar.users.filter(pk=user.id):
                    memeWar.users.add(request.user)
                memeWar.save()
                if reply_user_id is not None:
                    message = Message()
                    message.sender = request.user
                    message.receiver = get_object_or_404(User, pk=reply_user_id)
                    message.thread_meme = memeWar
                    message.save()
            new_meme_war = MemeWar()
            new_meme_war.thread_meme = new_meme
            new_meme_war.save()
            new_meme_war.users.add(request.user)
            new_meme_war.save()
            print('image uploaded')
            new_meme_id = new_meme.pk
            if thread_id.__len__() != 0:
                return redirect(reverse('meme_war', kwargs={'thread_id': thread_id}))

            return redirect(reverse('view_new_meme', kwargs={'meme_id': new_meme_id}))
    else:
        return redirect(reverse('new-meme'))


@login_required
@transaction.atomic
def new_meme_with_id(request, meme_bg_id):
    context = {}
    user = request.user
    first_name = user.first_name
    last_name = user.last_name
    context['curr_user_full_name'] = first_name + ' ' + last_name
    context['meme_bg_id'] = meme_bg_id
    if request.method == 'GET':
        context['form'] = NewMemeForm()
        context['user'] = request.user
    return render(request, 'core/editting.html', context)


@login_required
def view_new_meme(request, meme_id):
    context = {}
    user = request.user
    context['curr_user_full_name'] = user.first_name + ' ' + user.last_name
    context['meme_id'] = meme_id
    meme_obj = MemeObject.objects.get(pk=meme_id)
    context['meme_title'] = meme_obj.title
    context['user_id'] = request.user.id
    context['meme'] = meme_obj
    context['user'] = user
    return render(request, 'core/new_meme_view.html', context)


@login_required
def show_meme_photo(request, meme_id):
    this_meme = get_object_or_404(MemeObject, pk=meme_id)
    if not this_meme.image:
        raise Http404
    content_type = guess_type(this_meme.image.name)
    return HttpResponse(this_meme.image, content_type=content_type)


@login_required
def get_meme_bg(request, meme_bg_id):
    this_meme_bg = get_object_or_404(MemeBackground, pk=meme_bg_id)
    if not this_meme_bg.image:
        raise Http404
    content_type = guess_type(this_meme_bg.image.name)
    return HttpResponse(this_meme_bg.image, content_type=content_type)


@transaction.atomic
def signup(request):
    context = {}

    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        context['form'] = SignUpForm()
        return render(request, 'core/sign_up.html', context)

    form = SignUpForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'core/sign_up.html', context)

    # Creates the new user from the valid form data
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'])
    # Get rid of the if statement later
    if 'first_name' in request.POST:
        new_user.first_name = form.cleaned_data['first_name']
    if 'last_name' in request.POST:
        new_user.last_name = form.cleaned_data['last_name']

    new_user.is_active = False
    new_user.email = form.cleaned_data['email']
    new_user.save()
    new_profile = Profile(owner=new_user)
    new_profile.save()

    # new_user = authenticate(username=request.POST['username'], \
    #                         password=request.POST['password1'])
    # login(request, new_user)
    # return redirect(reverse('home'))
    context = {'user_id': new_user.id, 'host': request.get_host()}
    html_content = render_to_string('core/activation.html', context)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives('Activation', text_content, settings.EMAIL_HOST_USER, [new_user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return render(request, 'core/registration_confirm.html')


@login_required
def setting(request):
    context = {}
    if request.method == 'GET':
        setting_form = UpdateInfoForm()
        setting_form.fields['user_id'].initial = request.user.id
        context['setting_form'] = setting_form
        context['user'] = request.user
        return render(request, 'core/setting.html', context)
    return


@login_required
def update_info(request):
    main_user = request.user
    if request.method != 'POST':
        return redirect('/rememeber/setting')
    update_form = UpdateInfoForm(request.POST, request.FILES)
    if not update_form.is_valid():
        return redirect('/rememeber/setting')
    user = User.objects.get(pk=main_user.id)
    if update_form.cleaned_data.get('first_name'):
        user.first_name = update_form.cleaned_data.get('first_name')
    if update_form.cleaned_data.get('last_name'):
        user.last_name = update_form.cleaned_data.get('last_name')
    if update_form.cleaned_data.get('email'):
        user.email = update_form.cleaned_data.get('email')
    if update_form.cleaned_data.get('password1'):
        user.set_password(update_form.cleaned_data.get('password1'))
    if update_form.cleaned_data.get('image'):
        user.profile.image = update_form.cleaned_data.get('image')
    user.save()
    user.profile.save()
    return redirect('/rememeber/setting')


@login_required
def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    context = {}
    meme_list = MemeObject.objects.filter(owner=user).order_by('-created_at')
    like_list = MemeObject.objects.filter(liked_list=user).order_by('-created_at')
    war_list = user.user_war_list.all()
    context['meme_list'] = meme_list
    context['like_list'] = like_list
    context['war_list'] = war_list
    context['user'] = user
    context['user_id'] = user_id
    return render(request, 'core/UserProfile.html', context)


@login_required
def get_photo(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    image = user.profile.image
    if not image:
        raise Http404
    content_type = guess_type(image.name)
    return HttpResponse(image, content_type=content_type)


def get_profile_background(request):
    # temp_profile = Profile.objects.first()
    temp_profile = Profile()
    image = temp_profile.image
    if not image:
        raise Http404
    content_type = guess_type(image.name)
    return HttpResponse(image, content_type=content_type)


@login_required
def favorite(request, meme_id):
    meme = MemeObject.objects.get(pk=meme_id)
    user = request.user
    user.profile.liked_memes.add(meme)
    meme.liked_list.add(user)
    user.profile.save()
    count = meme.popularity_score
    new_count = count + 1
    meme.popularity_score = new_count
    meme.save()
    context = {}
    context['meme_id'] = meme_id
    context['count'] = new_count
    return render(request, 'core/add_favorite.json', context, content_type='application/json')


@login_required
def meme_war(request, thread_id):
    context = {}
    main_meme = get_object_or_404(MemeObject, pk=thread_id)
    thread = get_object_or_404(MemeWar, thread_meme=main_meme)
    meme_war_object = thread.meme_list.all()
    candidate = MemeObject.objects.filter(owner=request.user)
    context['thread_meme'] = main_meme
    context['meme_list'] = meme_war_object
    context['user'] = request.user
    context['candidate'] = candidate
    context['user_list'] = thread.users.all()
    return render(request, 'core/memewar.html', context)


@login_required
def create_meme_in_meme_war(request, thread_id, user_id):
    return new_meme(request, thread_id=thread_id, user_id=user_id)


@login_required
def reply_in_meme_war(request, thread_id, meme_id, user_id=None):
    main_meme = MemeObject.objects.get(pk=thread_id)
    meme_war = MemeWar.objects.get(thread_meme=main_meme)
    added_meme = MemeObject.objects.get(pk=meme_id)
    meme_war.meme_list.add(added_meme)
    meme_war.users.add(request.user)
    meme_war.save()
    if user_id is not None:
        message = Message()
        message.sender = request.user
        message.receiver = get_object_or_404(User, pk=user_id)
        message.thread_meme = meme_war
        message.save()
    return redirect(reverse('meme_war', kwargs={'thread_id': thread_id}))


@login_required
def sort_meme(request, string='recent'):
    if string == 'oldest':
        meme_list = MemeObject.objects.all().order_by('created_at')
    elif string == 'best':
        meme_list = MemeObject.objects.all().order_by('-popularity_score')
    elif string == 'worst':
        meme_list = MemeObject.objects.all().order_by('popularity_score')
    elif string == 'best_in_one_day':
        now = timezone.now()
        before = now - timezone.timedelta(days=1)
        meme_list = MemeObject.objects.filter(created_at__range=[before, now]).order_by('-popularity_score')
    else:
        meme_list = MemeObject.objects.all().order_by('-created_at')
    context = {}
    user = request.user
    context['user'] = user
    context['user_id'] = user.id
    context['meme_list'] = meme_list
    return render(request, 'core/MainStream.html', context)


@login_required
def search(request):
    if request.method != 'GET':
        return reverse('home')
    query = request.GET['query'].lower()
    if len(query.strip()) == 0:
        return reverse('home')
    meme_list = []
    all_meme_list = list(MemeObject.objects.all())
    for meme in all_meme_list:
        if meme.title.lower().__contains__(query) or meme.tags.lower().__contains__(query) \
                or meme.captions.lower().__contains__(query):
            meme_list.append(meme)
    context = {}
    user = request.user
    context['user'] = user
    context['user_id'] = user.id
    context['meme_list'] = meme_list
    return render(request, 'core/MainStream.html', context)


@login_required
def edit_meme(request, meme_bg_id):
    context = {}
    user = request.user
    first_name = user.first_name
    last_name = user.last_name
    context['curr_user_full_name'] = first_name + ' ' + last_name
    background = MemeBackground.objects.get(pk=meme_bg_id)
    background_library_all = list(MemeBackground.objects.filter(created_by=request.user))
    background_library = []
    path_library = []
    for bg in background_library_all:
        path = bg.image.url
        if path not in path_library:
            background_library.append(bg)
            path_library.append(path)
    if request.method == 'GET':
        form = NewMemeForm()
        context['form'] = form
        context['user'] = request.user
        context['meme_bg_lib'] = background_library
        if background is not None:
            context['meme_bg_id'] = meme_bg_id
    return render(request, 'core/editting.html', context)


@login_required
def get_notified(request):
    message_list = Message.objects.filter(receiver=request.user, has_read=False)
    context = {'notification_list': message_list}
    return render(request, 'core/notification.json', context, 'application/json')


@login_required
def read_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    message.has_read = True
    message.save()
    meme_war_id = message.thread_meme.id
    return redirect(reverse('meme_war', kwargs={'thread_id': meme_war_id}))


def activate(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    password = user.password
    username = user.username
    user.is_active = True
    user.save()
    return render(request, 'core/activation_confirm.html')


