# Instagram Cookie Extraction

These cookies are needed for both `yt-dlp` (metadata/download) and `instaloader` (video URL extraction).

## Automatic (preferred, works for Chrome)

The catalog script calls `yt-dlp --cookies-from-browser chrome` automatically.
This works **only if**:
1. The user is logged into Instagram on Chrome
2. The macOS Keychain has authorized cookie access at least once

The first access per boot may take 8-10 seconds while Keychain resolves.
The script's subprocess timeout is 25s.

## Manual (fallback)

### Get non-httpOnly cookies (Console tab, `document.cookie`)

```javascript
document.cookie
```
Copy the full output. This gives `csrftoken`, `ds_user_id`, `wd`, `ig_nrcb`, `mid`, etc.  
**Will NOT give** `sessionid` (httpOnly).

### Get httpOnly `sessionid` cookie (Application tab)

1. DevTools → **Application** tab (or `»` menu if hidden)
2. Left sidebar → **Storage → Cookies → https://www.instagram.com**
3. Find row where **Name** = `sessionid`
4. Double-click the **Value** cell → Cmd+C to copy
5. Paste just that value

### Full cookie file (Netscape format)

Used by `yt-dlp --cookies <file>`:

```
.instagram.com	TRUE	/	TRUE	1764081200	ig_nrcb	1
.instagram.com	TRUE	/	TRUE	1764081200	csrftoken	<value>
.instagram.com	TRUE	/	TRUE	1764081200	ds_user_id	<value>
.instagram.com	TRUE	/	TRUE	1764081200	sessionid	<value>
.instagram.com	TRUE	/	TRUE	1764081200	wd	150x682
```

### Instaloader session

```python
import instaloader
loader = instaloader.Instaloader()
loader.context._session.cookies.update({
    'sessionid': '<value>',
    'csrftoken': '<value>',
    'ds_user_id': '<value>',
})
```

## Cookie expiry

Instagram session cookies typically last 30-90 days. After that, the user must
re-authenticate and provide fresh cookies.

## Browser support

| Browser | Auto-extraction | Notes |
|---------|----------------|-------|
| Chrome  | `--cookies-from-browser chrome` | May trigger macOS Keychain dialog; add 8-10s |
| Edge    | `--cookies-from-browser edge` | Faster access, no keychain dialog |
| Safari  | Not tested | - |
