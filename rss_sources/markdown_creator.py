import pytz
from datetime import datetime
from rss_sources.config import SourceConfig
from rss_sources.models import Source, SourceCategory, Feed
from rss_sources.templates import TITLE_TEMPLATE, TABLE_START, TABLE_END, YOUTUBE_CUSTOM_TEMPLATE
from rss_sources.utils import parse_logger

from rss_sources.blogs import *
from rss_sources.youtube import *
from rss_sources.urls import *

from rss_sources.database.base import session


class Markdown:

    def __init__(self, sources):
        self.sources = sources \
            if isinstance(sources, list) else [sources]

    def create(self, title, feed_template, display_numbers, title_level=SourceConfig.TITLE_LEVEL):
        markdown_text = ''

        feeds = []

        for source in self.sources:
            # request 작업
            fetch_feeds = source.fetch_feeds()
            # DB 작업
            for feed in fetch_feeds:
                # 0) db로의 처리를 위해 sourcecategory / source / feed 형태 잡아주기
                # - SourceCategory정보를 feed['source']내부 source_category 객체로 만들어주기 ( 임시 )
                feed['source']['source_category'] = SourceCategory.get_or_create(
                    name=self.__class__.__name__.replace('Markdown', '')
                )
                # - source dict를 Source객체로 바꿔주기 + url로만 존재여부 판단하기
                feed['source'] = Source.get_or_create(**feed['source'], get_key='url')

                # 1) url로 필터링 + title이 달라질 경우는 update
                prev_feed = Feed.query.filter_by(url=feed['url']).first()
                if prev_feed:
                    if feed['title'] != prev_feed.title:
                        print(feed, "url존재하지만 title이 수정되어 변경만")
                        prev_feed.update(**feed)
                    continue

                feeds.append(Feed(**feed))


        if not feeds:
            parse_logger.info(f'{self.__class__.__name__}에서 feed가 하나도 없어 Markdown 생성이 안되었습니다.')
            return markdown_text

        session.add_all(feeds)
        session.commit()

        feeds = self.sort_and_truncate_feeds(feeds, display_numbers=display_numbers)

        # updated_at = pytz.timezone('Asia/Seoul').localize(datetime.now())
        # kst로 바로 localize하니까, strftime이 안찍히는 듯
        utc_updated_at = pytz.utc.localize(datetime.now())
        kst_updated_at = utc_updated_at.astimezone(pytz.timezone('Asia/Seoul'))
        markdown_text += TITLE_TEMPLATE.format(title_level, title, kst_updated_at.strftime("%Y-%m-%d %H:%M:%S"))
        markdown_text += self.set_custom()
        markdown_text += TABLE_START
        markdown_text += self.set_feed_template(feed_template, feeds, prefix=self.is_many_sources_or_targets())
        markdown_text += TABLE_END

        return markdown_text

    def is_many_sources_or_targets(self):
        if issubclass(self.__class__, URLMarkdown):
            return False

        # youtube의 경우, 1source고정이니, 여러 target-> prefix가 필요하다
        # 그외 tistory나 naver 둘중에 1개의 source만 취하는 경우 -> target이 여러개인 경우 필요하다?!
        if len(self.sources) == 1:
            return len(self.sources[0].target_id_with_categories) > 1
        # source가 여러개인 경우 -> naver + tistory -> prefix가 필요하다.
        elif len(self.sources) > 1:
            return True
        else:
            return False

    @staticmethod
    def sort_and_truncate_feeds(feeds, display_numbers):
        feeds.sort(key=lambda f: f['published'], reverse=True)

        return feeds[:display_numbers]

    def set_custom(self):
        return ''

    def set_feed_template(self, feed_template, feeds, prefix=None):
        raise NotImplementedError


class YoutubeMarkdown(Markdown):
    def __init__(self, target_ids):
        if not target_ids:
            raise ValueError(f'YoutubeMarkdown에 입력된 target_ids들이 존재하지 않습니다.')
        super().__init__(Youtube(target_ids))

    def set_custom(self):
        custom_result = ''
        for source in self.sources:
            if len(source.target_id_with_categories) == 1 and source.target_id_with_categories[0][0].startswith('UC'):
                custom_button = YOUTUBE_CUSTOM_TEMPLATE.format(source.target_id_with_categories[0][0])
                custom_result += custom_button

        return custom_result

    def set_feed_template(self, feed_template, feeds, prefix=None):
        feed_template_result = ''

        for feed in feeds:
            feed_text = feed_template.format(
                feed['url'],
                feed['thumbnail_url'],
                feed['url'],
                feed['title'],
                f'<span style="color:black">{feed["source_category_name"]} | </span>' if prefix else '',
                feed['published_string']
            )
            feed_template_result += feed_text

        return feed_template_result


class BlogMarkdown(Markdown):
    def __init__(self, tistory_targets=None, naver_targets=None):
        sources = []
        if self.check_targets(tistory_targets):
            sources.append(Tistory(tistory_targets))
        if self.check_targets(naver_targets):
            sources.append(Naver(naver_targets))

        if not sources:
            raise ValueError(f'BlogMarkdown에 입력된 target들이 존재하지 않습니다.')

        super().__init__(sources)

    @staticmethod
    def check_targets(targets):
        return [target_id for target_id, category in targets if target_id]

    def set_feed_template(self, feed_template, feeds, prefix=None):
        feed_template_result = ''

        for feed in feeds:
            feed_text = feed_template.format(
                feed['url'],
                feed['thumbnail_url'],
                feed['url'],
                feed['title'],
                f'{feed["source_category_name"]} | ' if prefix else '',
                feed['published_string']
            )
            feed_template_result += feed_text

        return feed_template_result


class URLMarkdown(Markdown):

    def __init__(self, url_and_names):
        sources = [globals()[name](url) for url, name in url_and_names]
        if not sources:
            raise ValueError(f'URLMarkdown에 입력된 url_and_names들이 존재하지 않습니다.')
        super().__init__(sources)

    def set_feed_template(self, feed_template, feeds, prefix=None):
        feed_template_result = ''
        for feed in feeds:
            feed_text = feed_template.format(
                feed['source_category_url'],
                feed['source_category_name'],
                f"{feed['category']}" if feed['category'] else '',
                feed['url'],
                feed['title'],
                feed['published_string']
            )
            feed_template_result += feed_text

        return feed_template_result
