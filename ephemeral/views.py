from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from .models import Ephemera, NGList, EphemeraURL, EphemeraDomain
from accounts.models import User
from django.views import generic
from django.views.generic.edit import ModelFormMixin
from django.views.generic import CreateView, UpdateView, ListView
from django.utils.safestring import mark_safe
import requests
from bs4 import BeautifulSoup
import json
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import EditMyListForm
from django.urls import reverse_lazy
from urllib.parse import urlparse


IMAGE_MIMETYPES = [
	'image/jpeg', 'image/gif', 'image/bmp', 'image/png'
]

#投稿されたURLをスクレイピング、サイトURLならオリジナルURL・タイトル・アイコン・サムネ取得
def scraping(url):
	r = requests.get(url)
	if r.headers['content-type'] and "text/html" in r.headers['content-type']:
		soup = BeautifulSoup(r.content, 'lxml')
		html = soup.find('link', rel="canonical")
		if html is None:
			site_url = url
		else:
			site_url = html.attrs['href']

		site_title = soup.title.string

		site_img = soup.find('meta', property="og:image")

		if site_img is None:
			site_img = "ephemera/default.png"
		else:
			site_img = site_img.get('content')
			if "http" in site_img:
				site_img = site_img
			elif "//" in site_img:
				site_img = "https:" + site_img
			else:
				site_img = site_url + site_img


		site_icon = soup.find("link", rel="shortcut icon")
		print(site_icon)

		if site_icon is None:
			site_icon = soup.find("link", rel="icon")

		if site_icon is None:
			site_icon = "ephemera/default_icon.png"
		else:
			site_icon = site_icon.attrs['href']
			if "http" in site_icon:
				site_icon = site_icon
			elif "//" in site_icon:
				site_icon = "https:" + site_icon
			else:
				site_icon = site_url + site_icon


	elif r.headers['content-type'] == "application/pdf":
		site_url   = url
		site_title = "PDFファイル"
		site_img   = "ephemera/default.png"
		site_icon  = "ephemera/default_icon.png"

	elif r.headers['content-type'] in IMAGE_MIMETYPES:
		site_url   = url
		site_title = "画像ファイル"
		site_img   = url
		site_icon  = "ephemera/default_icon.png"

	else:
		site_url   = "unknown"
		site_title = "unknown"
		site_img   = "unknown"
		site_icon  = "unknown"

	return {"site_url" : site_url, "site_title" : site_title, "site_img" : site_img, "site_icon" : site_icon, }

# Create your views here.
class Home(generic.ListView):
	model = Ephemera
	template_name = 'ephemeral/home.html'

	def paginator_setting(self, search, query_set, count):
		paginator = Paginator(query_set, count)  
		try:
			page = int(self.request.GET.get(search))
		except:
			page = 1
		try:
			query_set = paginator.page(page)
		except PageNotAnInteger:
			query_set = paginator.page(1)
		except EmptyPage:
			query_set = paginator.page(paginator.num_pages)

		return query_set

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		ephemeral_list = EphemeraURL.objects.annotate(Count('ephemera')).order_by('-ephemera__count')
		context['ephemeral_list'] = self.paginator_setting("page", ephemeral_list, 10)
		my_ephemeral_list = Ephemera.objects.filter(ep_user = self.request.user.id)
		context['my_ephemeral_list_url'] = my_ephemeral_list.values_list("url", flat=True)
		context["my_ephemeral_list"] = self.paginator_setting("my_list", my_ephemeral_list, 10)
		context["error_message"] = ""
		context["key_word"] = ""
		context["popular_domain"] = EphemeraDomain.objects.annotate(Count('domain')).order_by('-domain__count')[:5]
		return context

	def post(self, request):
		ephemeral_list = EphemeraURL.objects.annotate(Count('ephemera')).order_by('-ephemera__count')
		ephemeral_list = self.paginator_setting("page", ephemeral_list, 10)
		my_ephemeral_list = Ephemera.objects.filter(ep_user = self.request.user.id)
		my_ephemeral_list_url = my_ephemeral_list.values_list("url", flat=True)
		my_ephemeral_list = self.paginator_setting("my_list", my_ephemeral_list, 10)
		error_message = ""

		url        = request.POST.get('ep_url')
		my_ep_list = Ephemera.objects.filter(ep_user = self.request.user.id).values_list("url", flat=True)
		if url in my_ep_list :
			return render(request, 'ephemeral/home.html', {"error_message":"登録済みURLです", "ephemeral_list": ephemeral_list, "my_ephemeral_list":my_ephemeral_list, "my_ephemeral_list_url":my_ephemeral_list_url} )
		site       = scraping(url)
		message    = request.POST.get('ep_message')
		if message == "":
			message = site["site_title"]
		site_url   = site["site_url"]
		site_title = site["site_title"]
		site_img   = site["site_img"]
		site_icon  = site["site_icon"]
		ephemera_url = EphemeraURL.objects.filter(site_url = site_url).first()
		if ephemera_url == None:
			ephemera_url = EphemeraURL.objects.create(site_url=site_url)
		ephemera   = Ephemera.objects.create(ep_user=request.user, url=url, message=message, site_url=ephemera_url, site_title=site_title, site_img=site_img, site_icon=site_icon)
		
		parsed_url = urlparse(site_url)
		base_url = '{0.scheme}://{0.netloc}/'.format(parsed_url)
		ep_domain = EphemeraDomain.objects.create(domain=base_url)

		return redirect('ephemeral:home')


class Search(Home):
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		key_word = self.request.GET['word']
		if key_word == "new_ephemera":
			ephemeral_list = EphemeraURL.objects.all().annotate(Count('ephemera')).order_by('-ephemera__post_time')
		elif key_word == "ephemerandom":
			ephemeral_list = EphemeraURL.objects.all().annotate(Count('ephemera')).order_by('?')
		elif key_word == "random_user":
			random_user_id = Ephemera.objects.all().annotate(Count('ep_user')).order_by('ep_user').distinct()
			print(random_user_id)
			ephemeral_list = EphemeraURL.objects.filter(ephemera__ep_user=random_user_id[0].ep_user)
		else:
			ephemeral_list = EphemeraURL.objects.filter(Q(site_url__icontains=key_word)|Q(ephemera__message__icontains=key_word)|Q(ephemera__site_title__icontains=key_word)).annotate(Count('ephemera')).order_by('-ephemera__count')
		context['ephemeral_list'] = self.paginator_setting("page", ephemeral_list, 10)
		context["key_word"] = key_word
		return context

class MyList(generic.ListView):
	model = Ephemera
	template_name = 'ephemeral/mylist.html'

	def paginator_setting(self, search, query_set, count):
		paginator = Paginator(query_set, count)  
		try:
			page = int(self.request.GET.get(search))
		except:
			page = 1
		try:
			query_set = paginator.page(page)
		except PageNotAnInteger:
			query_set = paginator.page(1)
		except EmptyPage:
			query_set = paginator.page(paginator.num_pages)

		return query_set

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		my_ephemeral_list = Ephemera.objects.filter(ep_user = self.request.user.id)
		context['my_ephemeral_list_url'] = my_ephemeral_list.values_list("url", flat=True)

		context["my_ephemeral_list"] = self.paginator_setting("my_list", my_ephemeral_list, 10)
		
		return context

class EditMyList(generic.UpdateView):
	model = Ephemera
	template_name = 'ephemeral/mylist_edit.html'
	form_class = EditMyListForm
	success_url = reverse_lazy('ephemeral:mylist')

class DeleteMyList(generic.DeleteView):
	model = Ephemera
	success_url = reverse_lazy('ephemeral:mylist')