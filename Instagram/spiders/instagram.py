import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from Instagram.items import InstagramItem

'https://scontent-hel3-1.cdninstagram.com/v/t51.2885-19/s150x150/220876855_961950107935896_1586235541370066808_n.jpg' \
'?_nc_ht=scontent-hel3-1.cdninstagram.com&_nc_ohc=U5omh7qfXy4AX8DipY4&edm=ALB854YBAAAA&ccb=7-4&oh' \
'=05e78ee6c44305c79353d41322403f4c&oe=613CCBB4&_nc_sid=04cb80 '

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    inst_login_url = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = '89671239795'
    inst_pass = '#PWD_INSTAGRAM_BROWSER:10:1630930819:AUxQANtZG4f6FWQ4wqRExQ3ZorIpvQZyb3EM+S8SCvU8x8wsUmBN4/g0p4CiNaJe8X5y+63mZSlPQdTuzSHO7+VnsbAnQAw/lHPJFU2aRRcEhx2DsKye1sjNWuIKr0fC2FBEYh7SZ2caiw=='
    users_list = ['htmlacademy', 'y_practicum']
    api_url = 'https://i.instagram.com/api/v1/friendships/'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_url,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_pass},
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            for user in self.users_list:
                yield response.follow(f'/{user}/',
                                      callback=self.parse_user,
                                      cb_kwargs={'username': deepcopy(user)})

    def parse_user(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'count': 12}
        url_followers = f'{self.api_url}{user_id}/followers/?{urlencode(variables)}'
        url_following = f'{self.api_url}{user_id}/following/?{urlencode(variables)}'
        yield response.follow(url_followers,
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables)})
        yield response.follow(url_following,
                              callback=self.user_following_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables)})

    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        if j_data.get('next_max_id'):
            variables['max_id'] = j_data.get('next_max_id')
            variables['search_surface'] = 'follow_list_page'
            url_followers = f'{self.api_url}{user_id}/followers/?{urlencode(variables)}'
            yield response.follow(url_followers,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables)})
            followers = j_data.get('users')
            for follower in followers:
                item = InstagramItem(user_id=user_id,
                                     username=username,
                                     type='followers',
                                     follower_id=follower.get('pk'),
                                     follower_name=follower.get('username'),
                                     follower_photo=follower.get('profile_pic_url'))
                yield item

    def user_following_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        if j_data.get('next_max_id'):
            variables['max_id'] = j_data.get('next_max_id')
            variables['search_surface'] = 'follow_list_page'
            url_following = f'{self.api_url}{user_id}/following/?{urlencode(variables)}'
            yield response.follow(url_following,
                                  callback=self.user_following_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables)})
            following = j_data.get('users')
            for follow in following:
                item = InstagramItem(user_id=user_id,
                                     username=username,
                                     type='following',
                                     follower_id=follow.get('pk'),
                                     follower_name=follow.get('username'),
                                     follower_photo=follow.get('profile_pic_url'))
                yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
