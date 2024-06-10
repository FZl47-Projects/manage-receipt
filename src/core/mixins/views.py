import abc

from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.views.generic.base import TemplateResponseMixin

from core.utils import create_form_messages, log_event


class BaseCUViewMixin(abc.ABC):
    """
        Base Create & Update View Mixin
    """
    form = None
    success_message = _('Operation completed successfully')
    is_success = False
    redirect_url = None

    def do_success(self):
        pass

    def do_fail(self):
        pass

    def do_before_form_check(self):
        pass

    def get_redirect_url(self):
        if not self.redirect_url:
            self.redirect_url = self.request.META.get('HTTP_REFERER', '/')  # referrer url

        # add object url to redirect url
        obj = getattr(self, 'obj', None)
        if obj:
            try:
                self.redirect_url += f"?next_url={obj.get_dashboard_absolute_url()}"
            except (TypeError, ValueError, AttributeError):
                log_event('There is Some issue in add next_url(object dashboard absolute url) to redirect url',
                          'WARNING', exc_info=True)
        return self.redirect_url

    def set_success_message(self):
        if self.success_message:
            messages.success(self.request, self.success_message)

    def get_data(self, **kwargs):
        data = self.request.POST.copy()
        # add request to data
        data['request'] = self.request
        data.update(**kwargs)
        self.add_additional_data(data)
        self.data = data
        return data

    def add_additional_data(self, data, obj=None):
        pass

    def get_form(self):
        return self.form


class CreateViewMixin(BaseCUViewMixin):

    def do_before_create(self):
        pass

    def post(self, request, *args, **kwargs):
        data = self.get_data(**kwargs)
        f = self.get_form()(data=data, files=request.FILES)
        self.form_init = f
        self.do_before_form_check()
        if not f.is_valid():
            # create error message's
            create_form_messages(request, f)
            self.do_fail()
            return redirect(self.get_redirect_url())
        self.do_before_create()
        self.obj = f.save()
        self.is_success = True
        self.do_success()
        self.set_success_message()
        return redirect(self.get_redirect_url())


class UpdateViewMixin(BaseCUViewMixin):

    @abc.abstractmethod
    def get_object(self):
        pass

    def get_data(self, obj=None, **kwargs):
        data = self.request.POST.copy()
        # add request to data
        data['request'] = self.request
        data.update(**kwargs)
        self.add_additional_data(data, obj)
        self.data = data
        return data

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        data = self.get_data(obj)
        f = self.get_form()(instance=obj, data=data, files=request.FILES)
        self.form_init = f
        self.do_before_form_check()
        if not f.is_valid():
            # create error message's
            create_form_messages(request, f)
            self.do_fail()
            return redirect(self.get_redirect_url())
        self.obj = f.save()
        self.is_success = True
        self.do_success()
        self.set_success_message()
        return redirect(self.get_redirect_url())


class CreateOrUpdateViewMixin(UpdateViewMixin, abc.ABC):

    def is_create_state(self):
        obj = self.get_object()
        if obj:
            return False
        return True


class UpdateMultipleObjViewMixin(BaseCUViewMixin):
    ignore_err = False
    _updated_objects = None

    @abc.abstractmethod
    def get_objects(self):
        pass

    def _to_updated(self, obj):
        if not self._updated_objects:
            self._updated_objects = []
        self._updated_objects.append(obj)

    def get_updated_objects(self):
        return self._updated_objects

    def post(self, request):
        objects = self.get_objects()
        if objects is None:
            raise ValueError(' `get_objects` function must return a sequence(QuerySet or ..) not None type')
        for obj in objects:
            f = self.form(instance=obj, data=request.POST, files=request.FILES)
            if not f.is_valid():
                # create error message's
                create_form_messages(request, f)
                self.do_error()
                if not self.ignore_err:
                    return redirect(self.get_redirect_url())
                continue
            obj = f.save()
            self._to_updated(obj)
        self.do_success()
        self.set_success_message()
        return redirect(self.get_redirect_url())


class FilterSimpleListViewMixin(abc.ABC):
    search_param: str = 'search'
    search_fields: list | tuple = None
    filter_param: str = 'filter'
    filter_fields: list | tuple = None
    filter_param_all: str = 'all'

    def normalize_field_value(self, field_value):
        if field_value == 'true':
            field_value = True
        elif field_value == 'false':
            field_value = False
        return field_value

    def search(self, objects):
        if not self.search_fields:
            return objects
        sp = self.request.GET.get(self.search_param)
        if not sp:
            return objects

        query = Q()
        for field in self.search_fields:
            query |= Q(**{field: sp})
        objects = objects.filter(query)
        return objects

    def filter(self, objects):
        fp = self.request.GET.get(self.filter_param)
        if not fp:
            return objects
        if not self.filter_fields:
            return objects

        filter_fields_kw = {}
        for field in self.filter_fields:
            field_value = self.request.GET.get(field)
            if (not field_value) or (field_value == self.filter_param_all):
                continue
            field_value = self.normalize_field_value(field_value)
            filter_fields_kw[field] = field_value
        objects = objects.filter(**filter_fields_kw)
        return objects


class DeleteViewMixin(abc.ABC):
    success_message = _('Operation completed successfully')
    is_success = False
    redirect_url = None

    def do_success(self):
        pass

    def do_fail(self):
        pass

    def get_redirect_url(self):
        if not self.redirect_url:
            self.redirect_url = self.request.META.get('HTTP_REFERER', '/')  # referrer url
        return self.redirect_url

    @abc.abstractmethod
    def get_object(self, request, *args, **kwargs):
        pass

    def set_success_message(self):
        messages.success(self.request, self.success_message)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object(request, *args, **kwargs)
        if not obj:
            self.do_fail()
            self.is_success = False
            return redirect(self.get_redirect_url())
        obj.delete()
        self.is_success = True
        self.do_success()
        self.set_success_message()
        return redirect(self.get_redirect_url())


class MultipleUserViewMixin(abc.ABC, TemplateResponseMixin):
    user_template = None
    super_user_template = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_user_context(self):
        pass

    def get_super_user_context(self):
        pass

    def get_context(self):
        user = self.request.user
        if user.role == 'super_user':
            return self.get_super_user_context()
        elif user.role == 'normal_user':
            return self.get_user_context()

    def get_template_names(self):
        usr_role = self.request.user.role
        if usr_role == 'super_user':
            tmp = self.super_user_template
        else:
            tmp = self.user_template
        if tmp is None:
            raise PermissionDenied

            # raise ValueError(
            #     "TemplateResponseMixin requires either a definition of "
            #     "'super_user_template' or 'user_template' an implementation of 'get_template_names()'"
            # )

        return [tmp]

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied
        self.extra_context = self.get_context()
        return super().dispatch(request, *args, **kwargs)


class MultipleUserListViewMixin(MultipleUserViewMixin):

    def get_super_user_queryset(self):
        return []

    def get_user_queryset(self):
        return []

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_user':
            return self.get_super_user_queryset()
        elif user.role == 'normal_user':
            return self.get_user_queryset()


class UserRoleViewMixin(abc.ABC):

    @property
    @abc.abstractmethod
    def role_access(self):
        pass

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied
        if user.role not in self.role_access:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PermissionObjectsMixin(abc.ABC):
    QS_BY_PERMISSION = None
    USER_PERMISSIONS = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.USER_PERMISSIONS = []

    def get_user_perm(self):
        return self.request.user

    def get_qs_permission(self, *args, **kwargs):
        return self.QS_BY_PERMISSION

    def get_context_perm(self, *args, **kwargs):
        context = {}
        user = self.get_user_perm()

        for perm, dict_qs in self.get_qs_permission(*args, **kwargs).items():
            if user.has_perm(perm):
                qs = dict_qs.get('queryset')
                name = dict_qs.get('name')
                if qs is None or name is None:
                    raise ValueError(
                        'You should define `queryset` and `name` field in %s.QS_BY_PERMISSION ' % self.__class__.__name__)
                if not context.get(name):
                    context[name] = qs
                self.USER_PERMISSIONS.append(perm)
        return context
