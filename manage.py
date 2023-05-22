from rss_sources import create_database, get_current_services, fetch_all_service, parse_logger

# db.sqlite가 없으면 생성
create_database()

# 사용지정된 service객체들만 가져오기
services = get_current_services()

markdown_text = ''
for service in services:
    try:
        new_feeds = service.fetch_new_feeds()
    except Exception as e:
        parse_logger.info(f'{str(e)}', exc_info=True)

    markdown_text += service.render()

with open('./readme.md', 'w', encoding="UTF-8") as readme:
    with open('./default.md', 'r', encoding="UTF-8") as default:
        readme.write(default.read() + '\n')

    readme.write(markdown_text)
