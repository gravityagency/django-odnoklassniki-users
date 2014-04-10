# -*- coding: utf-8 -*-
from django.db import models, transaction
try:
    from django.db.transaction import atomic
except ImportError:
    from django.db.transaction import commit_on_success as atomic
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from datetime import datetime
from odnoklassniki_api.utils import api_call, OdnoklassnikiError
from odnoklassniki_api import fields
from odnoklassniki_api.decorators import fetch_all
from odnoklassniki_api.models import OdnoklassnikiManager, OdnoklassnikiPKModel
from odnoklassniki_places.models import City, Country
from dateutil import parser
from datetime import timedelta, datetime
import logging

log = logging.getLogger('odnoklassniki_users')

# USERS_INFO_TIMEOUT_DAYS = getattr(settings, 'VKONTAKTE_USERS_INFO_TIMEOUT_DAYS', 0)
#
# USER_FIELDS = 'uid,first_name,last_name,nickname,screen_name,sex,bdate,city,country,timezone,photo,photo_medium,photo_big,has_mobile,rate,contacts,education,activity,relation,wall_comments,relatives,interests,movies,tv,books,games,about,connections,universities,schools'
USER_SEX_CHOICES = ((1, u'жен.'), (2, u'муж.'))
# USER_RELATION_CHOICES = (
#     (1, u'Не женат / замужем'),
#     (2, u'Есть друг / подруга'),
#     (3, u'Помолвлен / помолвлена'),
#     (4, u'Женат / замужем'),
#     (5, u'Всё сложно'),
#     (6, u'В активном поиске'),
#     (7, u'Влюблён / влюблена'),
# )
#
# USER_PHOTO_DEACTIVATED_URL = 'http://vk.com/images/deactivated_'
# USER_NO_PHOTO_URL = 'http://vkontakte.ru/images/camera_'
#
# def list_chunks_iterator(l, n):
#     """ Yield successive n-sized chunks from l.
#     """
#     for i in xrange(0, len(l), n):
#         yield l[i:i+n]

# class ParseUsersMixin(object):
#     '''
#     Manager mixin for parsing response with extra cache 'profiles'. Used in vkontakte_wall,vkontakte_board applications
#     '''
#     def parse_response_users(self, response_list):
#         users = User.remote.parse_response_list(response_list.get('profiles', []), {'fetched': datetime.now()})
#         instances = []
#         for instance in users:
#             instances += [User.remote.get_or_create_from_instance(instance)]
#         return instances

class UsersManager(models.Manager):
    pass

#     def deactivated(self):
#         return self.filter(is_deactivated=True)
#
#     def active(self):
#         return self.filter(is_deactivated=False)
#
#     def with_avatar(self):
#         return self.filter(has_avatar=True)
#
#     def without_avatar(self):
#         return self.filter(has_avatar=False)

class UsersRemoteManager(OdnoklassnikiManager):

    fields = [
        'uid',
        'first_name',
        'last_name',
        'name',
        'gender',
        'birthday', #(yyyy-MM-dd)
        'age',
        'locale', #(en, lv, ... [language[_territory][.codeset][@modifier]] )
        'location',
        'current_status', # (текст статуса)
        'current_status_id', # (уникальный идентификатор статуса)
        'current_status_date', # (дата создания статуса)
        'online',
        'last_online',
        'photo_id', # - id главной фотографии
#         'pic_1', # - то же что и pic50x50
#         'pic_2', # - то же что и pic128max
#         'pic_3', # - то же что и pic190x190
#         'pic_4', # - то же что и pic640x480
#         'pic_5', # - то же что и pic128x128
        'pic50x50', # - квадратная аватарка 50x50
        'pic128x128', # - квадратная аватарка 128x128
        'pic128max', # - аватарка, вписанная в квадрат 128x128
        'pic180min', # - аватарка, заресайзенная по минимальной стороне 180
        'pic240min', # - аватарка, заресайзенная по минимальной стороне 240
        'pic320min', # - аватарка, заресайзенная по минимальной стороне 320
        'pic190x190', # - квадратная аватарка 190x190
        'pic640x480', # - аватарка, вписанная в квадрат 640x480
        'pic1024x768', # - аватарка, вписанная в квадрат 1024x768
        'url_profile',
        'url_profile_mobile',
        'url_chat',
        'url_chat_mobile',
        'has_email',
        'allows_anonym_access',
        'registered_date',
        'private',
        'has_service_invisible',
    ]
    fetch_users_limit = 100

    @atomic
    def fetch(self, ids, empty_pictures=True, **kwargs):
        # TODO: enlarge limit for only 100 users
        kwargs['uids'] = ','.join(map(lambda i: str(i), ids))
        if 'fields' not in kwargs:
            kwargs['fields'] = ','.join(self.fields)
        # Если true, не возвращает изображения Odnoklassniki по умолчанию, когда фотография пользователя недоступна
        kwargs['emptyPictures'] = empty_pictures

        return super(UserRemoteManager, self).fetch(**kwargs)

#     @transaction.commit_on_success
#     def fetch(self, **kwargs):
#         '''
#         Additional attributes:
#          * only_expired - flag to fetch only users, fetched earlie than VKONTAKTE_USERS_INFO_TIMEOUT_DAYS days ago
#         '''
#         if 'only_expired' in kwargs and kwargs.pop('only_expired'):
#             ids = kwargs['ids']
#             expired_at = datetime.now() - timedelta(USERS_INFO_TIMEOUT_DAYS)
#             ids_non_expired = self.model.objects.filter(fetched__gte=expired_at, remote_id__in=ids).values_list('remote_id', flat=True)
#             kwargs['ids'] = list(set(ids).difference(set(ids_non_expired)))
#             users = None
#             if len(kwargs['ids']):
#                 users = self._fetch(**kwargs)
#             return self._renew_queryset(users, ids)
#         else:
#             return self._fetch(**kwargs)
#
#     def _fetch(self, **kwargs):
#         '''
#         Method gives ability to fetch more than 1000 users at once
#         '''
#         ids = kwargs.pop('ids', None)
#         if ids:
#             kwargs_sliced = dict(kwargs)
#             for chunk in list_chunks_iterator(ids, self.fetch_users_limit):
#                 kwargs_sliced['ids'] = chunk
#                 users = super(UsersRemoteManager, self).fetch(**kwargs_sliced)
#
#             return self._renew_queryset(users, ids)
#         else:
#             return super(UsersRemoteManager, self).fetch(**kwargs)
#
#     def _renew_queryset(self, users, ids):
#         '''
#         Return argument `users` if ammount of `users` is equal to ammount `ids` we need to fetch
#         '''
#         if users is not None and len(ids) == users.count():
#             return users
#         else:
#             return self.model.objects.filter(remote_id__in=ids)
#
#     def api_call(self, method='get', **kwargs):
#         '''
#         Override parent behaviour without namespace property
#         TODO: move all kwargs manipulations to fetch method
#         '''
#         if 'fields' not in kwargs:
#             kwargs['fields'] = USER_FIELDS
#         if 'ids' in kwargs:
#             kwargs['uids'] = ','.join(map(lambda i: str(i), kwargs.pop('ids')))
#
#         return super(UsersRemoteManager, self).api_call(method, **kwargs)
#
#     def get_by_slug(self, slug):
#         '''
#         Return active user by slug
#         '''
#         try:
#             return super(UsersRemoteManager, self).get_by_slug(slug)
#         except self.model.MultipleObjectsReturned:
#             # fetch again all users with this slug and return only active one
#             self.model.remote.fetch(ids=[u.remote_id for u in self.model.objects.filter(screen_name=slug)])
#             return self.model.objects.active().get(screen_name=slug)
#
#     def parse_response_list(self, response_list, extra_fields=None):
#         if extra_fields and 'only_ids' in extra_fields:
#             return self.model.objects.filter(remote_id__in=response_list)
#         else:
#             return super(UsersRemoteManager, self).parse_response_list(response_list, extra_fields)

#    def get_or_create_from_instance(self, instance):
#        #DatabaseError: invalid byte sequence for encoding "UTF8": 0xeda0bc
#        #HINT:  This error can also happen if the byte sequence does not match the encoding expected by the server, which is controlled by "client_encoding".
#        # u.activity = u'\u041d\u0430\u0448 \u043e\u0431\u0443\u0447\u0430\u044e\u0449\u0438\u0439 \u043a\u0443\u0440\u0441 &quot;\u041a\u0430\u043a \u0438\u0437\u0431\u0430\u0432\u0438\u0442\u044c\u0441\u044f \u043e\u0442 \u0438\u043d\u0442\u0435\u0440\u043d\u0435\u0442-\u0437\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0441\u0442\u0438&quot; - \u0442\u0435\u043f\u0435\u0440\u044c \u0438 \u0432 \u043e\u043d\u043b\u0430\u0439\u043d \u0432\u0430\u0440\u0438\u0430\u043d\u0442\u0435\ud83c\u2708\ud83d\U0001f4a8'
#        if instance.remote_id != 59930666:
#            try:
#                super(UsersRemoteManager, self).get_or_create_from_instance(instance)
#            except DatabaseError, e:
#                log.error("Error while creating user with fields %s. Error: %s" % (instance.__dict__, e))
#
#        return instance

#    def get(self, *args, **kwargs):
#        '''
#        Apply country param request to all instances in reponse
#        '''
#        country = None
#
#        if 'country' in kwargs and self.model._meta.get_field('country'):
#            if isinstance(kwargs['country'], Country):
#                country = kwargs['country']
#            else:
#                country = Country.objects.get(remote_id=kwargs['country'])
#
#        instances = super(OdnoklassnikiPlacesManager, self).get(*args, **kwargs)
#
#        if country:
#            for instance in instances:
#                instance.country = country
#
#        return instances
#
#     @fetch_all(default_count=1000)
#     def fetch_likes_user_ids(self, likes_type, owner_id, item_id, offset=0, count=1000, filter='likes', *args, **kwargs):
#         if count > 1000:
#             raise ValueError("Parameter 'count' can not be more than 1000")
#         if filter not in ['likes', 'copies']:
#             raise ValueError("Parameter 'filter' should be equal to 'likes' or 'copies'")
#         if likes_type is None:
#             raise ImproperlyConfigured("'likes_type' attribute should be specified")
#
#         # type
#         # тип Like-объекта. Подробнее о типах объектов можно узнать на странице Список типов Like-объектов.
#         kwargs['type'] = likes_type
#         # owner_id
#         # идентификатор владельца Like-объекта (id пользователя или id приложения). Если параметр type равен sitepage, то в качестве owner_id необходимо передавать id приложения. Если параметр не задан, то считается, что он равен либо идентификатору текущего пользователя, либо идентификатору текущего приложения (если type равен sitepage).
#         kwargs['owner_id'] = owner_id
#         # item_id
#         # идентификатор Like-объекта. Если type равен sitepage, то параметр item_id может содержать значение параметра page_id, используемый при инициализации виджета «Мне нравится».
#         kwargs['item_id'] = item_id
#         # page_url
#         # url страницы, на которой установлен виджет «Мне нравится». Используется вместо параметра item_id.
#
#         # filter
#         # указывает, следует ли вернуть всех пользователей, добавивших объект в список "Мне нравится" или только тех, которые рассказали о нем друзьям. Параметр может принимать следующие значения:
#         # likes – возвращать всех пользователей
#         # copies – возвращать только пользователей, рассказавших об объекте друзьям
#         # По умолчанию возвращаются все пользователи.
#         kwargs['filter'] = filter
#         # friends_only
#         # указывает, необходимо ли возвращать только пользователей, которые являются друзьями текущего пользователя. Параметр может принимать следующие значения:
#         # 0 – возвращать всех пользователей в порядке убывания времени добавления объекта
#         # 1 – возвращать только друзей текущего пользователя в порядке убывания времени добавления объекта
#         # Если метод был вызван без авторизации или параметр не был задан, то считается, что он равен 0.
#         kwargs['friends_only'] = 0
#         # offset
#         # смещение, относительно начала списка, для выборки определенного подмножества. Если параметр не задан, то считается, что он равен 0.
#         kwargs['offset'] = int(offset)
#         # count
#         # количество возвращаемых идентификаторов пользователей.
#         # Если параметр не задан, то считается, что он равен 100, если не задан параметр friends_only, в противном случае 10.
#         # Максимальное значение параметра 1000, если не задан параметр friends_only, в противном случае 100.
#         kwargs['count'] = int(count)
#
#         log.debug('Fetching like users ids of %s %s_%s, offset %d' % (likes_type, owner_id, item_id, offset))
#
#         response = api_call('likes.getList', **kwargs)
#         return response['users']
#
#     @transaction.commit_on_success
#     def fetch_instance_likes(self, instance, *args, **kwargs):
#         '''
#         Deprecated. will be removed in next release, after updating vkontakte_photos app
#         '''
#         m2m_field_name = kwargs.pop('m2m_field_name', 'like_users')
#         m2m_model = getattr(instance, m2m_field_name).through
#         try:
#             rel_field_name = [field.name for field in m2m_model._meta.local_fields if field.name not in ['id','user']][0]
#         except IndexError:
#             raise ImproperlyConfigured("Impossible to find name of relation attribute for instance %s in m2m like users table" % instance)
#
#         ids = self.fetch_likes_user_ids(*args, **kwargs)
#         if not ids:
#             return self.none()
#
#         # fetch users
#         users = self.fetch(ids=ids, only_expired=True)
#
#         ids_current = m2m_model.objects.filter(**{rel_field_name: instance}).values_list('user_id', flat=True)
#         ids_new = users.values_list('pk', flat=True)
#         ids_left = set(ids_current).difference(set(ids_new))
#         ids_entered = set(ids_new).difference(set(ids_current))
#
#         # delete left
#         m2m_model.objects.filter(**{'user_id__in': ids_left, rel_field_name: instance}).delete()
#         # make entered
#         m2m_model.objects.bulk_create([m2m_model(**{'user_id': user_pk, rel_field_name: instance}) for user_pk in ids_entered])
#
#         return users


# class UserRelative(models.Model):
#
#     TYPE_CHOICES = (
#         ('grandchild', u'внук/внучка'),
#         ('grandparent',u'дедушка/бабушка'),
#         ('child', u'сын/дочка'),
#         ('sibling',u'брат/сестра'),
#         ('parent',u'мама/папа'),
#     )
#
#     user1 = models.ForeignKey('User', related_name='user_relatives1')
#     user2 = models.ForeignKey('User', related_name='user_relatives2')
#     type = models.CharField(u'Тип родственной связи', max_length=20, choices=TYPE_CHOICES)

class User(OdnoklassnikiPKModel):
    '''
    Model of vkontakte user
    TODO: implement relatives, schools and universities connections
    TODO: make field screen_name unique
    '''
    class Meta:
        verbose_name = _('Odnoklassniki user')
        verbose_name_plural = _('Odnoklassniki users')

#    resolve_screen_name_type = 'user'
    methods_namespace = 'users'
    remote_pk_field = 'uid'
    slug_prefix = 'profile'

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    shortname = models.CharField(max_length=100, db_index=True)

    gender = models.PositiveSmallIntegerField(null=True, choices=USER_SEX_CHOICES)
    birthday = models.CharField(max_length=100)
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    country_code = models.CharField(max_length=20)
    locale = models.CharField(max_length=5)

    photo_id = models.BigIntegerField(null=True)

    current_status = models.TextField()
    current_status_date = models.DateTimeField()
    current_status_id = models.BigIntegerField(null=True)

    allows_anonym_access = models.NullBooleanField()
    has_email = models.NullBooleanField()
    has_service_invisible = models.NullBooleanField()
    private = models.NullBooleanField()

    last_online = models.DateTimeField()
    registered_date = models.DateTimeField()

    photo_fields = ['pic1024x768', 'pic128max', 'pic128x128', 'pic180min', 'pic190x190', 'pic240min', 'pic320min', 'pic50x50', 'pic640x480']
    pic1024x768 = models.URLField()
    pic128max = models.URLField()
    pic128x128 = models.URLField()
    pic180min = models.URLField()
    pic190x190 = models.URLField()
    pic240min = models.URLField()
    pic320min = models.URLField()
    pic50x50 = models.URLField()
    pic640x480 = models.URLField()

    url_profile = models.URLField()
    url_profile_mobile = models.URLField()

    objects = UsersManager()
    remote = UserRemoteManager(methods={
        'get': 'getInfo',
    })

#     @property
#     def age(self):
#         try:
#             return int((datetime.today() - parser.parse(self.bdate)).days / 365.25)
#         except:
#             pass
#
#     def save(self, *args, **kwargs):
#         # check strings for good encoding
#         # there is problems to save users with bad encoded activity strings like ID=88798245, ID=143523733
#         for field in ['activity','games','movies','tv','books','about','interests','mobile_phone','home_phone','faculty_name','university_name']:
#             try:
#                 getattr(self, field).encode('utf-16').decode('utf-16')
#             except UnicodeDecodeError:
#                 setattr(self, field, '')
#
#         if self.relation and self.relation not in dict(USER_RELATION_CHOICES).keys():
#             self.relation = None
#
#         try:
#             return super(User, self).save(*args, **kwargs)
#         except Exception, e:
#             log.error("Error while saving user ID=%s with fields %s" % (self.remote_id, self.__dict__))
#             raise e
#
#     def _substitute(self, old_instance):
#         '''
#         Save counters fields while updating user
#         '''
#         for counter in self.counters:
#             setattr(self, counter, getattr(old_instance, counter))
#
#         self.sum_counters = old_instance.sum_counters
#         self.counters_updated = old_instance.counters_updated
#         self.friends_count = old_instance.friends_count
#         super(User, self)._substitute(old_instance)
#
#     def parse(self, response):
#
#         if 'city' in response:
#             self.city = City.objects.get_or_create(remote_id=response.pop('city'))[0]
#         if 'country' in response:
#             self.country = Country.objects.get_or_create(remote_id=response.pop('country'))[0]
#         if 'relatives' in response:
#             relatives = response.pop('relatives')
#             # doesn't work becouse of self.pk will be set lately
#             if self.pk:
#                 for relative in relatives:
#                     try:
#                         user_relative = UserRelative(type=relative.type, user1=self, user2=User.objects.get(remote_id=relative.uid))
#                         user_relative.save()
#                         self.relative.add(user_relative)
#                     except User.DoesNotExist:
#                         continue
#
#         super(User, self).parse(response)
#
#         self.parse_deactivated_status()
#         self.parse_avatar_presence()
#
# #        if 'uid' in response:
# #            self.remote_id = response['uid']
#
#         if self.graduation == 0:
#             self.graduation = None

    @property
    def refresh_kwargs(self):
        return {'ids': [self.pk]}

#     def parse_deactivated_status(self):
#         self.is_deactivated = False
#         for field_name in self.photo_fields:
#             if USER_PHOTO_DEACTIVATED_URL in getattr(self, field_name):
#                 self.is_deactivated = True
#                 return
#
#     def parse_avatar_presence(self):
#         self.has_avatar = True
#         for field_name in self.photo_fields:
#             if USER_NO_PHOTO_URL in getattr(self, field_name):
#                 self.has_avatar = False
#                 return

#     def update_counters(self):
#         '''
#         Update counters for user with special query and calculate sum of them
#         '''
#         try:
#             response = api_call('users.get', uids=self.remote_id, fields='counters')
#         except OdnoklassnikiError, e:
#             log.warning("There is vkontakte error [code=%d] while updating user [id=%d] counters: %s" % (e.code, self.remote_id, e.description))
#             return False
#
#         if 'counters' not in response[0]:
#             log.info("There is no counters field in response %s" % response)
#         else:
#             for counter in self.counters:
#                 if counter in response[0]['counters']:
#                     setattr(self, counter, response[0]['counters'][counter])
#
#             self.sum_counters = sum([getattr(self, counter) for counter in self.counters])
#         self.counters_updated = datetime.now()
#         self.save()

    def __unicode__(self):
        return self.name

#     def set_name(self, name):
#         name_parts = name.split()
#         self.first_name = name_parts[0]
#         if len(name_parts) > 1:
#             self.last_name = ' '.join(name_parts[1:])

#     def fetch_posts(self, *args, **kwargs):
#         if 'vkontakte_wall' not in settings.INSTALLED_APPS:
#             raise ImproperlyConfigured("Application 'vkontakte_wall' not in INSTALLED_APPS")
#
#         from vkontakte_wall.models import Post
#         return Post.remote.fetch_wall(owner=self, *args, **kwargs)
#
#     @transaction.commit_on_success
#     def fetch_friends(self, only_existing_users=False, **kwargs):
#         log.debug("Start updating friends of user %s" % self)
#         if self.is_deactivated:
#             return False
#
#         # send extra_fields with only_ids key for special mode of parsing response, used only in vkontakte_users.models
#         kwargs = {'fields': '', 'extra_fields': {'only_ids': True}} if only_existing_users else {'fields': 'uid,first_name,last_name,nickname,screen_name,sex,bdate,city,country,timezone,photo'}
#         try:
#             users = User.remote.fetch(method='friends', uid=self.remote_id, **kwargs)
#             log.debug("Found %d friends of user %s" % (len(users), self))
#         except OdnoklassnikiError, e:
#             if e.code == 15:
#                 # update current user, make him deactivated
#                 User.remote.fetch(uid=self.remote_id)
#                 return False
#             else:
#                 raise e
#
#         self.friends_users.clear()
#         log.debug("Cleared friends of user %s" % (self))
#
#         for user in users:
#             self.friends_users.add(user)
#         log.debug("New friends to user %s attached" % (self))
#
#         self.friends_count = self.friends_users.count()
#         self.save()
#         log.debug("Friends count %s of user %s updated" % (self.friends_count, self))
#
#         return self.friends_users.all()
#
#     def get_sex(self):
#         return dict(USER_SEX_CHOICES).get(self.sex)
#
# #    TODO: Solve naming, dublicate with boolean wall_comments
# #    @property
# #    def wall_comments(self):
# #        if 'vkontakte_wall' not in settings.INSTALLED_APPS:
# #            raise ImproperlyConfigured("Application 'vkontakte_wall' not in INSTALLED_APPS")
# #        from vkontakte_wall.models import Comment
# #        return Comment.objects.filter(remote_id__startswith='%s_' % self.remote_id)