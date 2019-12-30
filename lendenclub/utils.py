from datetime import datetime
from functools import wraps
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

class CustomDecorators:

    @staticmethod
    def paginate(get_context_data):
        @wraps(get_context_data)
        def wrapper(self, *args, **kwargs):
            self.__class__.context = super(self.__class__, self).get_context_data(**kwargs)
            self.__class__.context['now'] = datetime.now()
            object_list = self.__class__.model.objects.all()
            paginator = Paginator(object_list, self.__class__.paginate_by)
            page = self.request.GET.get('page')
            try:
                current_objects = paginator.page(page)
            except PageNotAnInteger:
                current_objects = paginator.page(1)
            except EmptyPage:
                current_objects = paginator.page(paginator.num_pages)
            self.__class__.context['object_list'] = current_objects
            return get_context_data(self)
        return wrapper