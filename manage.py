import os

from rss_sources import get_youtube_markdown, get_blog_markdown, get_url_markdown, parse_logger, SourceConfig
from rss_sources.database.base import Base, engine

if not os.path.isfile(os.path.basename(SourceConfig.DATABASE_URL)):
    # print(os.path.basename(SourceConfig.DATABASE_URL))
    # db.sqlite
    from rss_sources.models import *
    Base.metadata.create_all(bind=engine)

append_markdown = ''
append_markdown += get_youtube_markdown()
append_markdown += get_blog_markdown()
append_markdown += get_url_markdown()

if append_markdown:
    with open('./readme.md', 'w', encoding="UTF-8") as readme:
        with open('./default.md', 'r', encoding="UTF-8") as default:
            readme.write(default.read() + '\n')
        readme.write(append_markdown)

else:
    parse_logger.info('default readme에 추가할 내용이 없습니다.')
