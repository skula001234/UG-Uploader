import os
import requests
import subprocess
from vars import CREDIT
from pyrogram import Client, filters
from pyrogram.types import Message

#==================================================================================================================================

def extract_names_and_urls(file_content):
    lines = file_content.strip().split("\n")
    data = []
    for line in lines:
        if ":" in line:
            name, url = line.split(":", 1)
            data.append((name.strip(), url.strip()))
    return data

#==================================================================================================================================

def categorize_urls(urls):
    videos = []
    pdfs = []
    others = []

    for name, url in urls:
        new_url = url
        if "akamaized.net/" in url or "1942403233.rsc.cdn77.org/" in url:
            new_url = f"https://www.khanglobalstudies.com/player?src={url}"
            videos.append((name, new_url))
        elif "d1d34p8vz63oiq.cloudfront.net/" in url:
            new_url = f"https://anonymouspwplayer-0e5a3f512dec.herokuapp.com/pw?url={url}&token={your_working_token}"
            videos.append((name, new_url))
        elif "youtube.com/embed" in url:
            yt_id = url.split("/")[-1]
            new_url = f"https://www.youtube.com/watch?v={yt_id}"
            videos.append((name, new_url))
        elif ".m3u8" in url or ".mp4" in url:
            videos.append((name, url))
        elif "pdf" in url:
            pdfs.append((name, url))
        else:
            others.append((name, url))
    return videos, pdfs, others

#=================================================================================================================================

def generate_html(file_name, videos, pdfs, others):
    file_name_without_extension = os.path.splitext(file_name)

    sidebar_items = f'<li class="sidebar-item active">{file_name_without_extension}</li>'

    video_cards = "".join(
        f'''
        <div class="card">
            <span class="icon">🎞️</span>
            <span class="filename">{name}</span>
            <button class="button" onclick="playVideo('{url}')">Preview</button>
            <button class="button" onclick="window.open('{url}')">Download</button>
        </div>
        ''' for name, url in videos
    )

    pdf_cards = "".join(
        f'''
        <div class="card">
            <span class="icon">📑</span>
            <span class="filename">{name}</span>
            <button class="button" onclick="window.open('{url}')">Download</button>
            <a class="button" href="{url}" target="_blank">Open</a>
        </div>
        ''' for name, url in pdfs
    )

    other_cards = "".join(
        f'''
        <div class="card">
            <span class="icon">🌐</span>
            <span class="filename">{name}</span>
            <a class="button" href="{url}" target="_blank">Visit</a>
        </div>
        ''' for name, url in others
    )

    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>{file_name_without_extension} - Batch Content</title>
        <style>
            body {{ background: #16181A; color: #eee; font-family: 'Inter', Arial, sans-serif; margin: 0; }}
            .sidebar {{ width:220px; background: #20222F; height:100vh; position:fixed; top:0; left:0; padding:24px 12px; box-shadow:0 0 12px #0004; }}
            .sidebar h2 {{ color: #54B9FF; font-size:1.15em; margin-bottom:24px; }}
            .sidebar ul {{ list-style:none; margin:0; padding:0; }}
            .sidebar-item {{ padding: 12px 16px; font-size:1em; background:#23243a; margin-bottom:8px; border-radius:10px; color:#eee; cursor:pointer; transition:background .17s; }}
            .sidebar-item.active, .sidebar-item:hover {{ background:#2b2fcf; color:#fff; }}
            .main-content {{
                margin-left:240px; padding:36px 18px;
                display:flex; flex-direction:column;
            }}
            .search-bar {{
                width:100%; max-width:400px; font-size:1em; padding:10px; border-radius:12px; border:none; margin-bottom:24px;
                background: #23243a; color:#ececec; outline:none;
            }}
            .cards-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(265px, 1fr)); gap:24px; }}
            .card {{ background:#292B3A; border-radius:15px; padding:18px; box-shadow:0 2px 10px #0001; display:flex; flex-direction:column; align-items:flex-start; min-height:70px; }}
            .icon {{ font-size:1.45em; margin-bottom:8px; }}
            .filename {{ font-size:1.10em; margin-bottom:6px; color:#ffffffdd; font-weight:500; }}
            .button {{ margin-top:8px; margin-right:8px; background:#54B9FF; color:#181A20; border:none; padding:8px 16px; border-radius:10px; font-weight:600; cursor:pointer; transition:background .2s; }}
            .button:hover {{ background:#48E1DA; color:#101010; }}
            @media(max-width:650px) {{
                .sidebar {{ width:100vw; height:auto; position:relative; box-shadow:none; }}
                .main-content {{ margin-left:0; }}
                .cards-grid {{ gap:14px; }}
            }}
        </style>
        <script>
        function playVideo(url){{
            window.open(url, "_blank");
        }}
        function searchCards() {{
            var input = document.getElementById('search-bar').value.toLowerCase();
            var cards = document.querySelectorAll('.cards-grid .card');
            cards.forEach(function(card) {{
                var text = card.innerText.toLowerCase();
                card.style.display = text.includes(input) ? '' : 'none';
            }});
        }}
        </script>
    </head>
    <body>
        <div class="sidebar">
            <h2>Batch Topics</h2>
            <ul>
                {sidebar_items}
            </ul>
        </div>
        <div class="main-content">
            <input type="search" id="search-bar" class="search-bar" placeholder="Search videos, PDFs, links ..." oninput="searchCards()"/>
            <h2>🎞️ Videos</h2>
            <div class="cards-grid" id="videos">
                {video_cards}
            </div>
            <h2>📑 PDFs</h2>
            <div class="cards-grid" id="pdfs">
                {pdf_cards}
            </div>
            <h2>🌐 Other Links</h2>
            <div class="cards-grid" id="others">
                {other_cards}
            </div>
        </div>
    </body>
    </html>
    '''
    return html_template

#==================================================================================================================================

# Optional: Function to download video with FFmpeg
def download_video(url, output_path):
    command = f"ffmpeg -i {url} -c copy {output_path}"
    subprocess.run(command, shell=True, check=True)

#==================================================================================================================================

async def html_handler(bot: Client, message: Message):
    editable = await message.reply_text("𝐖𝐞𝐥𝐜𝐨𝐦𝐞! 𝐏𝐥𝐞𝐚𝐬𝐞 𝐮𝐩𝐥𝐨𝐚𝐝 𝐚 .𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐜𝐨𝐧𝐭𝐚𝐢𝐧𝐢𝐧𝐠 𝐔𝐑𝐋𝐬.✓")
    input: Message = await bot.listen(editable.chat.id)
    if input.document and input.document.file_name.endswith('.txt'):
        file_path = await input.download()
        file_name, ext = os.path.splitext(os.path.basename(file_path))
        b_name = file_name.replace('_', ' ')
    else:
        await message.reply_text("**• Invalid file input.**")
        return
           
    with open(file_path, "r") as f:
        file_content = f.read()

    urls = extract_names_and_urls(file_content)
    videos, pdfs, others = categorize_urls(urls)

    html_content = generate_html(file_name, videos, pdfs, others)
    html_file_path = file_path.replace(".txt", ".html")
    with open(html_file_path, "w") as f:
        f.write(html_content)

    await message.reply_document(
        document=html_file_path, 
        caption=f"🌐 𝐇𝐓𝐌𝐋 𝐅𝐢𝐥𝐞 𝐂𝐫𝐞𝐚𝐭𝐞𝐝!\n<blockquote><b>`{b_name}`</b></blockquote>\n🌟 Extracted By : {CREDIT}"
    )
    os.remove(file_path)
    os.remove(html_file_path)
