def serialize_work_list_item(work):
    primary = work.primary_media
    thumbnail = ""
    if primary and primary.file:
        thumbnail = primary.file.url

    return {
        "slug": work.slug,
        "title": work.title,
        "genre": {
            "name": work.genre.name,
            "slug": work.genre.slug,
        },
        "thumbnail": thumbnail,
        "created_date": work.created_date.isoformat() if work.created_date else None,
        "is_featured": work.is_featured,
    }


def serialize_work_detail(work):
    media_items = []
    for media in work.media.all():
        item = {
            "media_type": media.media_type,
            "caption": media.caption,
            "file_url": media.file.url if media.file else "",
            "external_url": media.external_url,
        }
        media_items.append(item)

    return {
        "slug": work.slug,
        "title": work.title,
        "description": work.description,
        "highlights_list": work.highlights_list,
        "created_date": work.created_date.isoformat() if work.created_date else None,
        "production_hours": work.production_hours,
        "tools": [tool.name for tool in work.tools.all()],
        "tags": [tag.name for tag in work.tags.all()],
        "genre": {
            "name": work.genre.name,
            "slug": work.genre.slug,
        },
        "media": media_items,
    }
