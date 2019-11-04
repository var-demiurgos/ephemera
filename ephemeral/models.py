from django.db import models
from accounts.models import User
# Create your models here.

class EphemeraURL(models.Model):
	site_url   = models.URLField()
	def __str__(self):
		return str(self.site_url)

class Ephemera(models.Model):
	ep_user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ep_user')
	url        = models.URLField()
	message    = models.TextField(max_length=200)
	post_time  = models.DateTimeField(auto_now_add = True)
	site_title = models.TextField(max_length=100)
	site_img   = models.TextField(max_length=1000, blank=True, default="static/ephemera/default.png") 
	site_icon  = models.TextField(max_length=1000, blank=True, default="static/ephemera/default_icon.png") 
	site_url   = models.ForeignKey(EphemeraURL, on_delete=models.CASCADE)

class EphemeraDomain(models.Model):
	domain     = models.URLField()
	post_time  = models.DateTimeField(auto_now_add = True)

class NGList(models.Model):
	claim_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claim_user')
	ng_user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ng_user')

	def __str__(self):
		return str(self.claim_user) + " → " + str(self.ng_user)