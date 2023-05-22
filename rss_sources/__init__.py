import os

from rss_sources.markdown_creator import YoutubeMarkdown, BlogMarkdown, URLMarkdown
from rss_sources.templates import YOUTUBE_FEED_TEMPLATE, BLOG_FEED_TEMPLATE, URL_FEED_TEMPLATE
from rss_sources.utils import parse_logger, db_logger

from rss_sources.config import SourceConfig
from rss_sources.services import YoutubeService, BlogService, URLService


def create_database():
    if not os.path.isfile(os.path.basename(SourceConfig.DATABASE_URL)):
        from rss_sources.models import SourceCategory, Source, Feed
        from rss_sources.database.base import Base, engine
        # print(os.path.basename(SourceConfig.DATABASE_URL)) db.sqlite
        db_logger.info('db파일을 최초 생성하였습니다.')
        Base.metadata.create_all(bind=engine)
    else:
        db_logger.info('기존 db파일이 있는 상태입니다.')


def fetch_all_service():
    try:
        youtube_service = YoutubeService()
        youtube_updated = youtube_service.fetch_new_feeds()
    except Exception as e:
        parse_logger.info(f'{str(e)}', exc_info=True)
    try:
        blog_service = BlogService()
        blog_updated = blog_service.fetch_new_feeds()
    except Exception as e:
        parse_logger.info(f'{str(e)}', exc_info=True)

    try:
        url_service = URLService()
        url_updated = url_service.fetch_new_feeds()
    except Exception as e:
        parse_logger.info(f'{str(e)}', exc_info=True)


def render_all_service(default_path='./default.md', readme_path='./readme.md'):
    youtube_service = YoutubeService()
    blog_service = BlogService()
    url_service = URLService()

    markdown_text = ''
    markdown_text += youtube_service.render()
    markdown_text += blog_service.render()
    markdown_text += url_service.render()

    with open(readme_path, 'w', encoding="UTF-8") as readme:
        with open(default_path, 'r', encoding="UTF-8") as default:
            readme.write(default.read() + '\n')
        readme.write(markdown_text)


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
        parse_logger.error(f'youtube markdown 생성 실패: {str(e)}', exc_info=True)
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
        parse_logger.error(f'blog markdown 생성 실패: {str(e)}', exc_info=True)
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
        parse_logger.error(f'url markdown 생성 실패: {str(e)}', exc_info=True)
        return ''


if __name__ == '__main__':
    create_database()

    from rss_sources.services import YoutubeService, BlogService, URLService

    #

    # print(youtube_updated)
    # print(blog_updated)
    # print(url_updated)
    youtube_service = YoutubeService()
    # youtube_service.get_feeds()
    print(youtube_service.render())

    blog_service = BlogService()
    print(blog_service.render())

    url_service = URLService()
    print(url_service.render())

    # {'id': 1, 'title': '임시 - 그룹웨어 핵심기능 - 부서관리 및 조직도',
    # 'url': 'https://www.youtube.com/watch?v=FoiRAZSHKUI',
    # 'thumbnail_url': 'https://i3.ytimg.com/vi/FoiRAZSHKUI/hqdefault.jpg',
    # 'category': None,
    # 'body': '',
    # 'published': datetime.datetime(2023, 5, 15, 7, 30, 29),
    # 'published_string': '2023년 05월 15일 16시 30분 29초',
    # 'source_id': 1,
    # 'created_at': datetime.datetime(2023, 5, 21, 16, 46, 7, 638418),
    # 'updated_at': datetime.datetime(2023, 5, 21, 16, 46, 7, 638418)}

    # append_markdown = ''
    # append_markdown += get_youtube_markdown()
    # append_markdown += get_blog_markdown()
    # append_markdown += get_url_markdown()
    #
    # if append_markdown:
    #     with open('../readme_test.md', 'w', encoding="UTF-8") as readme:
    #         with open('../default.md', 'r', encoding="UTF-8") as default:
    #             readme.write(default.read()+'\n')
    #         readme.write(append_markdown)
    #
    # else:
    #     parse_logger.info('default readme에 추가할 내용이 없습니다.')
