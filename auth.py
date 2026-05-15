import asyncio
import random


async def _human_type(page, selector, text):
    """Type text character by character with random delays."""
    await page.click(selector)
    await page.wait_for_timeout(random.randint(300, 600))
    for char in text:
        await page.keyboard.type(char)
        await page.wait_for_timeout(random.randint(80, 220))


async def login(page, url, username, password):
    """
    Navigate to url, detect login form, fill credentials
    with human-like typing, submit, and wait for navigation.

    Returns True if login likely succeeded, False otherwise.
    """
    print(f"[AUTH] Navigating to login page: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(random.randint(1000, 2000))

    # =========================================================
    # DETECT FIELDS
    # =========================================================

    user_selectors = [
        'input[type="email"]',
        'input[name="email"]',
        'input[name="username"]',
        'input[name="user"]',
        'input[id*="email"]',
        'input[id*="user"]',
        'input[placeholder*="email" i]',
        'input[placeholder*="username" i]',
    ]

    pass_selectors = [
        'input[type="password"]',
    ]

    submit_selectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Login")',
        'button:has-text("Sign in")',
        'button:has-text("Log in")',
    ]

    user_field = await _find_selector(page, user_selectors)
    pass_field = await _find_selector(page, pass_selectors)

    if not user_field or not pass_field:
        print("[AUTH] Could not detect login form fields")
        return False

    print(f"[AUTH] Found username field: {user_field}")
    print(f"[AUTH] Found password field: {pass_field}")

    # =========================================================
    # FILL FORM
    # =========================================================

    # move mouse to field area first (human-like)
    await page.hover(user_field)
    await page.wait_for_timeout(random.randint(200, 500))

    await _human_type(page, user_field, username)

    # pause between fields
    await page.wait_for_timeout(random.randint(500, 1200))

    await page.hover(pass_field)
    await page.wait_for_timeout(random.randint(200, 400))

    await _human_type(page, pass_field, password)

    # pause before submitting
    await page.wait_for_timeout(random.randint(800, 1500))

    # =========================================================
    # SUBMIT
    # =========================================================

    submit = await _find_selector(page, submit_selectors)

    if submit:
        print(f"[AUTH] Clicking submit: {submit}")
        await page.hover(submit)
        await page.wait_for_timeout(random.randint(200, 500))
        await page.click(submit)
    else:
        print("[AUTH] No submit button found, pressing Enter")
        await page.keyboard.press("Enter")

    # wait for navigation after login
    try:
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
    except Exception:
        pass

    await page.wait_for_timeout(random.randint(1500, 2500))

    # =========================================================
    # VERIFY
    # =========================================================

    current_url = page.url
    still_on_login = any(
        kw in current_url.lower()
        for kw in ("login", "signin", "sign-in", "auth")
    )

    if still_on_login:
        print("[AUTH] Still on login page — credentials may be wrong")
        return False

    print(f"[AUTH] Login successful. Now at: {current_url}")
    return True


async def capture_session(context, page):
    """
    After login, capture cookies + localStorage + sessionStorage.
    Returns a session dict to be passed to restore_session().
    """
    cookies = await context.cookies()

    storage = await page.evaluate("""() => {
        const local = {};
        const session = {};
        for (let i = 0; i < localStorage.length; i++) {
            const k = localStorage.key(i);
            local[k] = localStorage.getItem(k);
        }
        for (let i = 0; i < sessionStorage.length; i++) {
            const k = sessionStorage.key(i);
            session[k] = sessionStorage.getItem(k);
        }
        return { localStorage: local, sessionStorage: session };
    }""")

    # extract token-like keys for logging
    token_keys = [
        k for k in list(storage["localStorage"]) + list(storage["sessionStorage"])
        if any(t in k.lower() for t in ("token", "access", "refresh", "auth", "jwt"))
    ]
    cookie_names = [c["name"] for c in cookies]

    print(f"[AUTH] Session captured — cookies: {cookie_names}")
    if token_keys:
        print(f"[AUTH] Tokens found in storage: {token_keys}")

    return {
        "cookies": cookies,
        "localStorage": storage["localStorage"],
        "sessionStorage": storage["sessionStorage"],
    }


async def restore_session(context, page, session):
    """
    Inject captured session (cookies + storage) into a new page context.
    Call this before navigating to any authenticated page.
    """
    if not session:
        return

    # restore cookies at context level (persists across pages)
    if session.get("cookies"):
        await context.add_cookies(session["cookies"])

    # restore storage via JS (must be on same origin — navigate to blank first)
    local = session.get("localStorage", {})
    sess = session.get("sessionStorage", {})

    if local or sess:
        await page.evaluate("""([local, sess]) => {
            for (const [k, v] of Object.entries(local)) {
                try { localStorage.setItem(k, v); } catch(e) {}
            }
            for (const [k, v] of Object.entries(sess)) {
                try { sessionStorage.setItem(k, v); } catch(e) {}
            }
        }""", [local, sess])

    print("[AUTH] Session restored")


async def _find_selector(page, selectors):
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1000):
                return sel
        except Exception:
            continue
    return None
