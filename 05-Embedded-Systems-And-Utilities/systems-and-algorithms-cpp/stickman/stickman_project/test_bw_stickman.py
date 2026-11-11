import chrome_session
import time
import urllib.request
import os

page = chrome_session.get_or_open_page("bing.com/images/create", "https://www.bing.com/images/create", reuse=True)
old_url = page.url

prompt = (
    "minimalist black and white cartoon art, clean white background, two funny stickman characters: "
    "a boy stickman on the left and a girl stickman with simple cute ponytail on the right, "
    "having a funny expressive conversation, simple black ink lines, monochrome doodle style, "
    "minimalist stick figures, very minimal subtle color accent, no realistic human faces, pure stickman, masterpiece"
)

textarea = page.wait_for_selector("textarea[name='gmc__textarea'], textarea[placeholder*='Describe']", timeout=8000)
textarea.click()
textarea.press("Control+A")
textarea.press("Backspace")
textarea.type(prompt, delay=5)
time.sleep(0.5)

gen_btn = page.wait_for_selector("button:has-text('Generate'), button.gmbtn__btn", timeout=5000)
gen_btn.click()
print("Submitted B&W Boy & Girl prompt to Bing!")

for _ in range(30):
    time.sleep(1)
    if page.url != old_url and ("/1-" in page.url or "FORM=GENCRE" in page.url):
        break

print("Waiting for image to generate...")
img_src = None
for _ in range(40):
    time.sleep(1.5)
    img_src = page.evaluate("""() => {
        let display = document.querySelector('img.aigc-display__img');
        if (display && display.src && display.naturalWidth > 150) return display.src;
        let thumb = document.querySelector('img.aigc-batch__thumb');
        if (thumb && thumb.src && thumb.naturalWidth > 100) return thumb.src;
        let any_oig = Array.from(document.querySelectorAll('img')).find(i => 
            i.src && i.src.includes('th.bing.com') && i.src.includes('OIG') && i.naturalWidth > 150
        );
        return any_oig ? any_oig.src : null;
    }""")
    if img_src:
        break

if img_src:
    out_path = r"C:\Users\abdul\.gemini\antigravity\brain\a28b7e23-4a1d-490e-86cb-c5a75cf0dcb2\bw_boy_girl_test.png"
    clean_url = img_src.split("?")[0] + "?pid=ImgGn"
    req = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        with open(out_path, "wb") as f:
            f.write(resp.read())
    print("SUCCESS: Downloaded test image:", out_path)
else:
    print("FAILED: Image source not found")
