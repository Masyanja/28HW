import json

from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, UpdateView

from avito.settings import TOTAL_ON_PAGE
from users.models import User, Location


# Create your views here.
class UserListView(ListView):
    model = User

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.object_list = self.object_list.order_by('username')
        paginator = Paginator(self.object_list, TOTAL_ON_PAGE)
        page = request.GET.get('page')
        obj = paginator.get_page(page)
        response = {}
        items_list = [{'id': user.pk,
                       'username': user.username,
                       'first_name': user.first_name,
                       'last_name': user.last_name,
                       'role': user.role,
                       'age': user.age,
                       'locations': list(map(str, user.location.all())),
                       'total_ads': user.ads.filter(is_published=True).count()
                       } for user in obj]
        response['items'] = items_list
        response['total'] = self.object_list.count()
        response['num_pages'] = paginator.num_pages

        return JsonResponse(response, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        user = self.get_object()

        return JsonResponse({'id': user.pk,
                             'username': user.username,
                             'first_name': user.first_name,
                             'last_name': user.last_name,
                             'role': user.role,
                             'age': user.age,
                             'locations': list(map(str, user.location.all())),
                             'total_ads': user.ads.filter(is_published=True).count()
                             }, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ['username']

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        data = json.loads(request.body)
        if 'first_name' in data:
            self.object.first_name = data['first_name']
        if 'last_name' in data:
            self.object.last_name = data['last_name']
        if 'role' in data:
            self.object.role = data['role']
        if 'age' in data:
            self.object.age = data['age']
        if 'locations' in data:
            for loc_name in data['locations']:
                loc, _ = Location.objects.get_or_create(name=loc_name)
                self.object.location.add(loc)
        self.object.save()
        return JsonResponse({'id': self.object.pk,
                             'username': self.object.username,
                             'first_name': self.object.first_name,
                             'last_name': self.object.last_name,
                             'role': self.object.role,
                             'age': self.object.age,
                             'locations': list(map(str, self.object.location.all()))
                             }, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class UserCreateView(CreateView):
    model = User
    fields = ['username']

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        data = json.loads(request.body)
        user = User.objects.create(
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            age=data['age']
        )

        if 'locations' in data:
            for loc_name in data['locations']:
                loc, _ = Location.objects.get_or_create(name=loc_name)
                user.location.add(loc)

        return JsonResponse({'id': user.pk,
                             'username': user.username,
                             'first_name': user.first_name,
                             'last_name': user.last_name,
                             'role': user.role,
                             'age': user.age,
                             'locations': list(map(str, user.location.all())),
                             }, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return JsonResponse({'status': 'ok'}, status=204)
