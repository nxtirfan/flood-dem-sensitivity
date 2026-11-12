"""Inspect the public GEE entry point without submitting login or changing scripts."""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

out = Path(__file__).resolve().parent
result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
          'requested_url': 'https://code.earthengine.google.com/',
          'context': 'new isolated Chromium context; no user session supplied',
          'login_submitted': False, 'gee_computation_executed': False}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    try:
        response = page.goto(result['requested_url'], wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(5000)
        url = urlsplit(page.url)
        result.update(http_status=response.status if response else None,
                      final_origin=f'{url.scheme}://{url.netloc}', final_path=url.path,
                      title=page.title(), password_inputs=page.locator('input[type=password]').count(),
                      email_inputs=page.locator('input[type=email]').count())
        body = page.locator('body').inner_text()
        result['sign_in_visible'] = 'sign in' in body.lower()
        result['body_excerpt'] = body[:1800]
        page.screenshot(path=str(out / 'gee_access.png'), full_page=False)
    except Exception as error:
        result['error_type'] = type(error).__name__
        result['error'] = str(error).split('Call log:')[0][:700]
    browser.close()
(out / 'browser_access.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
