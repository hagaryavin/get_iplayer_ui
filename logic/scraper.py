import requests
from bs4 import BeautifulSoup

def fetch_basic_info(pid):
    """
    מחזיר שם, תקציר ותמונה עבור תוכנית לפי PID — לשימוש בתוצאות חיפוש
    """
    url = f"https://www.bbc.co.uk/programmes/{pid}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('meta', property='og:title')
    description_tag = soup.find('meta', property='og:description')
    image_tag = soup.find('meta', property='og:image')

    title = title_tag['content'] if title_tag else "No title found"
    description = description_tag['content'] if description_tag else "No description found"
    image_url = image_tag['content'] if image_tag else None
    duration = "Unknown duration"
    meta_tags = soup.select('p.episode-panel__meta')
    for tag in meta_tags:
        text = tag.get_text(strip=True)
        if "minute" in text or "hour" in text:
            duration = text
            break
    return {
        'title': title,
        'description': description,
        'image': image_url,
        'duration':duration
    }

def fetch_detailed_info(pid):
    url = f"https://www.bbc.co.uk/programmes/{pid}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # שם התוכנית מתוך meta
    title_tag = soup.find('meta', property='og:title')
    programme_title = title_tag['content'] if title_tag else "Unknown programme title"

    # תיאור מתוך meta
    # תיאור: קודם HTML, אם לא נמצא — אז meta
    description = None
    long_desc_block = soup.select_one('.synopsis-toggle__long')
    if long_desc_block:
        paragraphs = long_desc_block.find_all('p')
        description = "\n".join(p.get_text(strip=True) for p in paragraphs)
    else:
        short_desc_block = soup.select_one('.synopsis-toggle__short p')
        if short_desc_block:
            description = short_desc_block.get_text(strip=True)

    # אם לא נמצא תיאור ב־HTML — נשלוף מה־meta
    if not description:
        meta_desc_tag = soup.find('meta', property='og:description')
        description = meta_desc_tag['content'] if meta_desc_tag else "No description available"
        
    # תמונה מתוך meta
    image_tag = soup.find('meta', property='og:image')
    image_url = image_tag['content'] if image_tag else None

    duration = "Unknown duration"
    meta_tags = soup.select('p.episode-panel__meta')
    for tag in meta_tags:
        text = tag.get_text(strip=True)
        if "minute" in text or "hour" in text:
            duration = text
            break

    # רשימת שירים
    tracks = []
    track_list_items = soup.select('li.segments-list__item')
    for li in track_list_items:
        artist_tag = li.select_one('h3 .artist')
        track_title_tag = li.select_one('p.no-margin span')

        artist = artist_tag.get_text(strip=True) if artist_tag else "Unknown artist"
        track_title = track_title_tag.get_text(strip=True) if track_title_tag else "Unknown title"

        track_str = f"{artist} - {track_title}"
        tracks.append(track_str)

    return {
        "title": programme_title,
        "description": description,
        "duration": duration,
        "tracks": tracks,
        "image": image_url
    }


