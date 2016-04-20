import urllib.request
from django.core.files.base import ContentFile
from complain.models import Account
from requests import request

def create_account(strategy, backend, user, response, details,
        is_new=False, *args, **kwargs):
    if is_new:
        acc = Account.objects.create(user=user)
        acc.verified = True
        acc.save()
        if backend.name == 'facebook':
            print(str(response))
            url = 'http://graph.facebook.com/{0}/picture'.format(response['id'])

            resp = request('GET', url, params={'type': 'large'})
            acc.profile_pic.save(str(acc.user.id)+'.jpg', ContentFile(resp.content))
            acc.save()

        elif backend.name == 'twitter':
            print(str(response))
            url = response['profile_image_url']
            url = url.replace('_normal','')
            resp = request('GET', url, params={})
            acc.profile_pic.save(str(acc.user.id)+'.jpg', ContentFile(resp.content))
            acc.save()

        elif backend.name == 'google-oauth2':
            url = response['image']['url']
            url = url.replace('?sz=50','?sz=250')
            resp = request('GET', url, params={})
            acc.profile_pic.save(str(acc.user.id)+'.jpg', ContentFile(resp.content))
            acc.save()


def save_profile_pic(strategy, backend, user, response, details,
        is_new=False, *args, **kwargs):
    if is_new and backend.name == 'facebook':
        url = 'http://graph.facebook.com/{0}/picture'.format(response['id'])

        try:
            resp = request('GET', url, params={'type': 'large'})
            resp.raise_for_status()
        except HTTPError:
            pass
        else:
            #redirect_url = reverse('new_social', kwargs={'uid':response['id']})
            url = '/complain/new-social/?'
            url += 'social=facebook&'
            url += 'uid='+response['id']
            url += 'userid='+str(user.id)
            return HttpResponseRedirect(url)

