from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import SignUpForm
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from .models import User
from ephemeral.models import Ephemera
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def sign_up(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('ephemeral:home')
	else:
		form = SignUpForm()
	return render(request, 'accounts/sign_up.html', {'form': form})

class MyPageView(LoginRequiredMixin, generic.TemplateView):
	template_name = 'accounts/mypage.html'

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
		context["my_ephemeral_list"] = self.paginator_setting("my_list", my_ephemeral_list, 12)
		return context