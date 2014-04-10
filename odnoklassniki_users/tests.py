# -*- coding: utf-8 -*-
from django.test import TestCase
from vkontakte_places.models import City, Country
from models import User, USER_PHOTO_DEACTIVATED_URL, USER_NO_PHOTO_URL, USERS_INFO_TIMEOUT_DAYS
from factories import UserFactory
from datetime import datetime, timedelta
import simplejson as json
import mock

USER_ID = 561348705024
USER_SCREEN_NAME = 'yevgeiny.durov'

# def user_fetch_mock(ids, **kwargs):
#     users = [User.objects.get(remote_id=id) if User.objects.filter(remote_id=id).count() == 1 else UserFactory(remote_id=id) for id in ids]
#     ids = [user.pk for user in users]
#     return User.objects.filter(pk__in=ids)

class VkontakteUsersTest(TestCase):

#     def test_refresh_user(self):
#
#         instance = User.remote.fetch(ids=[USER_ID])[0]
#         self.assertEqual(instance.screen_name, USER_SCREEN_NAME)
#
#         instance.screen_name = 'temp'
#         instance.save()
#         self.assertEqual(instance.screen_name, 'temp')
#
#         instance.refresh()
#         self.assertEqual(instance.screen_name, USER_SCREEN_NAME)
#
# #    def test_fetch_user_relatives(self):
# #
# #        users = User.remote.fetch(ids=[1,6])
# #
# #        instance = users[0]
# #
# #        self.assertEqual(instance.relatives.count(), 0)
# #
# #        users = User.remote.fetch(ids=[1,6])
# #
# #        self.assertEqual(instance.relatives.count(), 1) # fix it, design decision needed
# #        self.assertEqual(instance.relatives.all()[0], users[1])
#
#     def test_fetch_user_friends(self):
#
#         self.assertEqual(User.objects.count(), 0)
#         user = User.remote.fetch(ids=[6])[0]
#         self.assertEqual(User.objects.count(), 1)
#         user.fetch_friends()
#         self.assertTrue(User.objects.count() > 100)
#         self.assertEqual(user.friends_users.count(), User.objects.count()-1)
#
#     def test_fetch_user(self):
#
#         self.assertEqual(User.objects.count(), 0)
#         users = User.remote.fetch(ids=[1,2])
#         self.assertEqual(len(users), 2)
#         self.assertEqual(User.objects.count(), 2)
#
#         instance = users[0]
#
#         self.assertEqual(instance.remote_id, 1)
#         self.assertEqual(instance.first_name, u'Павел')
#         self.assertEqual(instance.last_name, u'Дуров')
#         self.assertEqual(instance.screen_name, USER_SCREEN_NAME)
# #        self.assertEqual(instance.twitter, u'durov')
# #        self.assertEqual(instance.livejournal, u'durov')
# #        self.assertEqual(instance.relation, 1)
#         self.assertEqual(instance.wall_comments, False)
#
#         # test counters
#         instance.update_counters()
#         self.assertTrue(instance.followers > 0)
#         self.assertTrue(instance.notes > 0)
#         self.assertTrue(instance.sum_counters > 0)
#         self.assertTrue(instance.counters_updated is not None)
#
#         # fetch another time
#         users = User.remote.fetch(ids=[1,2])
#         self.assertEqual(User.objects.count(), 2)
#
#         instance = users[0]
#
#         # test for keeping old counters
#         self.assertTrue(instance.sum_counters > 0)
#         self.assertTrue(instance.followers > 0)
#         self.assertTrue(instance.counters_updated is not None)
#
#     @mock.patch('vkontakte_api.models.VkontakteManager.fetch', side_effect=user_fetch_mock)
#     def test_fetch_users_more_than_1000(self, fetch):
#
#         users = User.remote.fetch(ids=range(0, 1500))
#         self.assertEqual(len(users), 1500)
#         self.assertEqual(User.objects.count(), 1500)
#
#         self.assertEqual(len(fetch.mock_calls[0].call_list()[0][2]['ids']), 1000)
#         self.assertEqual(len(fetch.mock_calls[1].call_list()[0][2]['ids']), 500)
#
#     @mock.patch('vkontakte_users.models.User.remote._fetch', side_effect=user_fetch_mock)
#     def test_fetching_expired_users(self, fetch):
#
#         users = User.remote.fetch(ids=range(0, 150))
#
#         # make all users fresh
#         User.objects.all().update(fetched=datetime.now())
#         # make 50 of them expired
#         User.objects.filter(remote_id__lt=50).update(fetched=datetime.now() - timedelta(USERS_INFO_TIMEOUT_DAYS + 1))
#
#         users_new = User.remote.fetch(ids=range(0, 150), only_expired=True)
#
#         self.assertEqual(len(fetch.mock_calls[0].call_list()[0][2]['ids']), 150)
#         self.assertEqual(len(fetch.mock_calls[1].call_list()[0][2]['ids']), 50)
#         self.assertEqual(users.count(), 150)
#         self.assertEqual(users.count(), users_new.count())
#
    def test_parse_user(self):

        response = u'''[{
              "allows_anonym_access": True,
              "birthday": "05-11",
              "current_status": "собщество генерал шермон",
              "current_status_date": "2013-11-12 03:45:01",
              "current_status_id": "62725470887936",
              "first_name": "Евгений",
              "gender": "male",
              "has_email": False,
              "has_service_invisible": False,
              "last_name": "Дуров",
              "last_online": "2014-04-09 02:35:10",
              "locale": "r",
              "location": {"city": "Кемерово",
               "country": "RUSSIAN_FEDERATION",
               "countryCode": "RU"},
              "name": "Евгений Дуров",
              "photo_id": "508669228288",
              "pic1024x768": "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=3&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic128max": "http://usd1.mycdn.me/getImage?photoId=508669228288&photoType=2&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic128x128": "http://umd1.mycdn.me/getImage?photoId=508669228288&photoType=6&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic180min": "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=13&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic190x190": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=5&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic240min": "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=14&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic320min": "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=15&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic50x50": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=4&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic640x480": "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=0&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_1": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=4&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_2": "http://usd1.mycdn.me/getImage?photoId=508669228288&photoType=2&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_3": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=5&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_4": "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=0&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_5": "http://umd1.mycdn.me/getImage?photoId=508669228288&photoType=6&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "private": False,
              "registered_date": "2012-11-05 14:13:53",
              "uid": "561348705024",
              "url_profile": "http://www.odnoklassniki.ru/profile/561348705024",
              "url_profile_mobile": "http://www.odnoklassniki.ru/profile/?st.application_key=CBAEBGLBEBABABABA&st.signature=d9867421a0017d9a08c17a206edf2730&st.reference_id=561348705024"}]'''

        instance = User()
        instance.parse(json.loads(response)[0])
        instance.save()

        self.assertEqual(instance.id, 561348705024)
        self.assertEqual(instance.name, u'Евгений Дуров')

        self.assertEqual(instance.allows_anonym_access, True)
        self.assertEqual(instance.birthday, "05-11")
        self.assertEqual(instance.current_status, u"собщество генерал шермон")
        self.assertEqual(instance.current_status_date, datetime(2013, 11, 12, 3, 45, 01))
        self.assertEqual(instance.current_status_id, 62725470887936)
        self.assertEqual(instance.first_name, u"Евгений")
        self.assertEqual(instance.gender, "male")
        self.assertEqual(instance.has_email, False)
        self.assertEqual(instance.has_service_invisible, False)
        self.assertEqual(instance.last_name, u"Дуров")
        self.assertEqual(instance.last_online, datetime(2014, 4, 9, 2, 35, 10))
        self.assertEqual(instance.locale, "r")
        self.assertEqual(instance.city, u"Кемерово")
        self.assertEqual(instance.country, "RUSSIAN_FEDERATION")
        self.assertEqual(instance.country_code, "RU")
        self.assertEqual(instance.name, u"Евгений Дуров")
        self.assertEqual(instance.photo_id, 508669228288)

        self.assertEqual(instance.pic1024x768, "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=3&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic128max, "http://usd1.mycdn.me/getImage?photoId=508669228288&photoType=2&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic128x128, "http://umd1.mycdn.me/getImage?photoId=508669228288&photoType=6&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic180min, "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=13&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic190x190, "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=5&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic240min, "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=14&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic320min, "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=15&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic50x50, "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=4&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic640x480, "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=0&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.private, False)
        self.assertEqual(instance.registered_date, datetime(2012, 11, 5, 14, 13, 53))
        self.assertEqual(instance.url_profile, "http://www.odnoklassniki.ru/profile/561348705024")
        self.assertEqual(instance.url_profile_mobile, "http://www.odnoklassniki.ru/profile/?st.application_key=CBAEBGLBEBABABABA&st.signature=d9867421a0017d9a08c17a206edf2730&st.reference_id=561348705024")


#     def test_parse_user(self):
#
#         response = '''
#             {"response":[{"city": "1025548",
#                   "country": "1",
#                   "faculty": "0",
#                   "faculty_name": "",
#                   "first_name": "\u041b\u0435\u043d\u0443\u0441\u0438\u043a",
#                   "graduation": "2000",
#                   "has_mobile": 1,
#                   "home_phone": "",
#                   "last_name": "\u0422\u0430\u0440\u0430\u043d\u0443\u0445\u0438\u043d\u0430",
#                   "mobile_phone": "8951859*1**",
#                   "online": 0,
#                   "photo": "%s",
#                   "photo_big": "http://cs9825.userapi.com/u51443905/a_f732002c.jpg",
#                   "photo_medium": "%s",
#                   "photo_medium_rec": false,
#                   "rate": "95",
#                   "screen_name": "id51443905",
#                   "sex": 1,
#                   "timezone": 3,
#                   "uid": 51443905,
#                   "university": "0",
#                   "university_name": ""}
#             ]}
#             ''' % (USER_PHOTO_DEACTIVATED_URL, USER_NO_PHOTO_URL)
#         instance = User()
#         instance.parse(json.loads(response)['response'][0])
#         instance.save()
#
#         self.assertEqual(instance.remote_id, 51443905)
#         self.assertEqual(instance.country, Country.objects.get(remote_id=1))
#         self.assertEqual(instance.city, City.objects.get(remote_id=1025548))
#         self.assertEqual(instance.faculty, 0)
#         self.assertEqual(instance.faculty_name, u'')
#         self.assertEqual(instance.first_name, u'Ленусик')
#         self.assertEqual(instance.graduation, 2000)
#         self.assertEqual(instance.has_mobile, True)
#         self.assertEqual(instance.home_phone, u'')
#         self.assertEqual(instance.last_name, u'Таранухина')
#         self.assertEqual(instance.mobile_phone, '8951859*1**')
#         self.assertEqual(instance.photo, USER_PHOTO_DEACTIVATED_URL)
#         self.assertEqual(instance.photo_big, 'http://cs9825.userapi.com/u51443905/a_f732002c.jpg')
#         self.assertEqual(instance.photo_medium, USER_NO_PHOTO_URL)
#         self.assertEqual(instance.photo_medium_rec, '')
#         self.assertEqual(instance.rate, 95)
#         self.assertEqual(instance.screen_name, u'id51443905')
#         self.assertEqual(instance.sex, 1)
#         self.assertEqual(instance.timezone, 3)
#         self.assertEqual(instance.university, 0)
#         self.assertEqual(instance.university_name, u'')
#         self.assertEqual(instance.is_deactivated, True)
#         self.assertEqual(instance.has_avatar, False)
#
#     def test_bad_activity(self):
#
#         bad_activity = u'\u7b7e\u8b49\u10e1\u502c\udd0c\u9387\ud157\uaf0c\ub348\ua8b7\uf0c7\uca16\ufd54\u3fb8\uabbd\u9b3c\u8329\u5630\uee9e\u5b81\u5976\u1c90\u7916\u56b9\u49fc\u4884\ua6b8\u3a6c\u6160\u1c6e\u1da1\udfe5\u254a\u25e3\ua933\u7e2f\u92c6\ubd1b\u9877\u2a56\uf3c6\uc03c\u5036\u336b\uef31\u3caf\u5c3c\ucba3\u0ad0\uca00\u9552\u7f4e\u2e4e\u5d24\u4b7c\ucf0e\u41ba\u20e2\u0d32\u1d81\ue82e\uc009\u2fad\udb67\ue8b2\ua3f2\ub71c\uc631\u9ad8\u3abd\u0364\u70d7\uc49c\u0d95\u02ec\u65c4\ucc5c\udee7\u45ca\ufe2a\u38a5\uca5f\uc398\ue37e\u117b\xd5\ua3e5\ue2bc\u8aab\u53df\ua98f\u580f\uc1c5\u66bc\u6d24\uacae\u3115\uc1d6\ufdfd\uadee\u71f6\u5c62\u9e9e\u685a\u9939\ud8e8\u191f\u96b5\u7a62\u7598\ud1e3\u4e39\u5328\u63c9\u808b\u5265\u9890\uaa48\u88dc\u6b67\u7b24\u8d70\ufdb1\ua387\u0747\u80a9\u9eb6\uea60\u8f56\u6ae2\u862c\u201c\u2eb8\u1fda\ufd58\u7d90\u0cd8\u2231\u0fc9\ucfd3'
#         User.objects.create(remote_id=1, activity=bad_activity, sex=0)
#         self.assertEqual(User.objects.count(), 1)
#         self.assertEqual(User.objects.all()[0].activity, '')
#
#         good_activity = u'Хорошая строка, good string'
#         User.objects.create(remote_id=2, activity=good_activity, sex=0)
#         self.assertEqual(User.objects.count(), 2)
#         self.assertEqual(User.objects.all()[1].activity, good_activity)
#
#     def test_multiple_slug_users(self):
#
#         User.objects.create(remote_id=173613533, screen_name='mikhailserzhantov', sex=0)
#         User.objects.create(remote_id=174221855, screen_name='mikhailserzhantov', sex=0)
#         User.objects.create(remote_id=182224356, screen_name='mikhailserzhantov', sex=0)
#
#         self.assertEqual(User.remote.get_by_slug('mikhailserzhantov').remote_id, 182224356)
#         self.assertEqual(User.objects.deactivated().count(), 2)
