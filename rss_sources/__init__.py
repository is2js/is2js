import os

from rss_sources.markdown_creator import YoutubeMarkdown, BlogMarkdown, URLMarkdown
from rss_sources.templates import YOUTUBE_FEED_TEMPLATE, BLOG_FEED_TEMPLATE, URL_FEED_TEMPLATE
from rss_sources.utils import parse_logger

from rss_sources.config import SourceConfig



def get_youtube_markdown():
    if not SourceConfig.youtube_target_ids:
        return ''

    try:
        youtube_markdown = YoutubeMarkdown(SourceConfig.youtube_target_ids)
        return youtube_markdown.create(
            title=SourceConfig.YOUTUBE_TITLE,
            feed_template=YOUTUBE_FEED_TEMPLATE,
            display_numbers=SourceConfig.YOUTUBE_DISPLAY_NUMBERS
        )

    except Exception as e:
        parse_logger.error(f'youtube markdown 생성 실패: {str(e)}')
        return ''


def get_blog_markdown():
    if not SourceConfig.tistory_target_id_and_categories and not SourceConfig.naver_target_id_and_categories:
        return ''

    try:
        blog_markdown = BlogMarkdown(
            tistory_targets=SourceConfig.tistory_target_id_and_categories,
            naver_targets=SourceConfig.naver_target_id_and_categories
        )
        return blog_markdown.create(
            title=SourceConfig.BLOG_TITLE,
            feed_template=BLOG_FEED_TEMPLATE,
            display_numbers=SourceConfig.BLOG_DISPLAY_NUMBERS
        )

    except Exception as e:
        parse_logger.error(f'blog markdown 생성 실패: {str(e)}')
        return ''


def get_url_markdown():
    if not SourceConfig.url_and_names:
        return ''

    try:
        url_markdown = URLMarkdown(
            # 민족의학신문("rss_url")
            # [globals()[name](url) for url, name in SourceConfig.url_and_names]
            SourceConfig.url_and_names
        )
        return url_markdown.create(
            title=SourceConfig.URL_TITLE,
            feed_template=URL_FEED_TEMPLATE,
            display_numbers=SourceConfig.URL_DISPLAY_NUMBERS
        )
    except Exception as e:
        parse_logger.error(f'url markdown 생성 실패: {str(e)}')
        return ''


def create_database():
    if not os.path.isfile(os.path.basename(SourceConfig.DATABASE_URL)):
        from rss_sources.models import Category, Source, Feed
        from rss_sources.database.base import Base, engine
        # print(os.path.basename(SourceConfig.DATABASE_URL))
        # db.sqlite
        Base.metadata.create_all(bind=engine)

if __name__ == '__main__':

    append_markdown = ''
    append_markdown += get_youtube_markdown()
    append_markdown += get_blog_markdown()
    append_markdown += get_url_markdown()

    if append_markdown:
        with open('../readme_test.md', 'w', encoding="UTF-8") as readme:
            with open('../default.md', 'r', encoding="UTF-8") as default:
                readme.write(default.read()+'\n')
            readme.write(append_markdown)

    else:
        parse_logger.info('default readme에 추가할 내용이 없습니다.')