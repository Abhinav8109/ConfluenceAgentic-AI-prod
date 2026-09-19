"""
Enhanced Confluence Automated Seeder Script
Publishes all 24 CloudOps knowledge pages to live Confluence Cloud in space 'AITEST'.
Renders rich, colorful XHTML with gradient banners, status macros, info callout cards,
styled comparison tables, and visual architecture diagrams.
"""

import sys
import os
import re
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.confluence.seed_data import SEED_PAGES

def get_page_theme(title: str):
    """Returns color schemes, badges, and icon based on page topic."""
    t = title.lower()
    if "gcp" in t or "google" in t:
        return {
            "gradient": "linear-gradient(135deg, #1a73e8, #0284c7)",
            "accent": "#1a73e8",
            "icon": "[GCP]",
            "badge1": ("GCP TIER-1", "Blue"),
            "badge2": ("ENTERPRISE", "Green"),
            "category": "Google Cloud Platform"
        }
    elif "aws" in t or "amazon" in t:
        return {
            "gradient": "linear-gradient(135deg, #232f3e, #f59e0b)",
            "accent": "#f59e0b",
            "icon": "[AWS]",
            "badge1": ("AWS HYBRID", "Yellow"),
            "badge2": ("ACTIVE MESH", "Blue"),
            "category": "Amazon Web Services"
        }
    elif "multi-cloud" in t or "hybrid" in t or "interconnect" in t:
        return {
            "gradient": "linear-gradient(135deg, #4f46e5, #06b6d4)",
            "accent": "#4f46e5",
            "icon": "[HYBRID]",
            "badge1": ("MULTI-CLOUD", "Blue"),
            "badge2": ("HA INTERCONNECT", "Green"),
            "category": "Multi-Cloud Networking"
        }
    elif "incident" in t or "security" in t or "escalation" in t or "vulnerability" in t:
        return {
            "gradient": "linear-gradient(135deg, #be123c, #e11d48)",
            "accent": "#e11d48",
            "icon": "[SECURITY]",
            "badge1": ("SECURITY SENSITIVE", "Red"),
            "badge2": ("24/7 ON-CALL", "Yellow"),
            "category": "Security & Incident Governance"
        }
    elif "database" in t or "sql" in t or "spanner" in t:
        return {
            "gradient": "linear-gradient(135deg, #047857, #10b981)",
            "accent": "#10b981",
            "icon": "[DATABASE]",
            "badge1": ("HIGH AVAILABILITY", "Green"),
            "badge2": ("ACID COMPLIANT", "Blue"),
            "category": "Database Operations"
        }
    else:
        return {
            "gradient": "linear-gradient(135deg, #1e293b, #3b82f6)",
            "accent": "#3b82f6",
            "icon": "[RUNBOOK]",
            "badge1": ("OPERATIONAL SOP", "Green"),
            "badge2": ("PRODUCTION VERIFIED", "Blue"),
            "category": "Operations & Runbooks"
        }
            "badge2": ("PRODUCTION VERIFIED", "Blue"),
            "category": "Operations & Runbooks"
        }

def markdown_to_confluence_storage_html(title: str, version: int, md: str) -> str:
    """
    Converts markdown content into high-fidelity, colorful Confluence Storage XHTML format.
    Includes top gradient hero banner, status badge chips, styled tables, code callouts,
    and info macro blocks.
    """
    theme = get_page_theme(title)
    
    # Hero Banner
    hero_banner = f"""
<div style="background: {theme['gradient']}; padding: 24px 28px; border-radius: 12px; color: #ffffff; margin-bottom: 24px; box-shadow: 0 8px 24px rgba(0,0,0,0.12);">
  <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(255,255,255,0.85); margin-bottom: 6px;">
    {theme['icon']} {theme['category']} &nbsp;|&nbsp; Version {version}.0
  </div>
  <h1 style="color: #ffffff; margin: 0 0 10px 0; font-size: 26px; font-weight: 800; letter-spacing: -0.02em;">
    {title}
  </h1>
  <p style="color: rgba(255,255,255,0.92); margin: 0; font-size: 14px; max-width: 780px; line-height: 1.6;">
    Authoritative operational specification connected live to the CloudOps AI Knowledge Assistant.
  </p>
  <div style="margin-top: 14px;">
    <ac:structured-macro ac:name="status" ac:schema-version="1">
      <ac:parameter ac:name="title">{theme['badge1'][0]}</ac:parameter>
      <ac:parameter ac:name="colour">{theme['badge1'][1]}</ac:parameter>
    </ac:structured-macro>
    &nbsp;
    <ac:structured-macro ac:name="status" ac:schema-version="1">
      <ac:parameter ac:name="title">{theme['badge2'][0]}</ac:parameter>
      <ac:parameter ac:name="colour">{theme['badge2'][1]}</ac:parameter>
    </ac:structured-macro>
  </div>
</div>
"""

    lines = md.strip().split("\n")
    html_lines = [hero_banner]
    in_code_block = False
    code_block_lines = []
    in_table = False
    first_h1_skipped = False

    for line in lines:
        stripped = line.strip()

        # Skip duplicate # Title heading since hero banner already has it
        if stripped.startswith("# ") and not first_h1_skipped:
            first_h1_skipped = True
            continue

        # Code blocks & diagrams
        if stripped.startswith("```"):
            if in_code_block:
                code_content = "\n".join(code_block_lines)
                code_content = code_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                html_lines.append(
                    f'<div style="background: #0f172a; border-radius: 8px; padding: 14px 18px; margin: 14px 0; border: 1px solid #334155; color: #f8fafc; overflow-x: auto;">'
                    f'<pre style="margin:0; font-family: monospace; font-size: 13px; line-height: 1.5;"><code>{code_content}</code></pre>'
                    f'</div>'
                )
                code_block_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_block_lines = []
            continue

        if in_code_block:
            code_block_lines.append(line)
            continue

        # Tables
        if stripped.startswith("|") and stripped.endswith("|"):
            if "---" in stripped:
                continue  # Divider row
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not in_table:
                in_table = True
                html_lines.append(
                    '<table style="width:100%; border-collapse: collapse; margin: 18px 0; font-size: 13px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.04);">'
                    '<thead><tr style="background: #1e293b; color: #ffffff;">'
                )
                th_cells = "".join([f'<th style="padding: 10px 14px; text-align: left; font-weight: 700; border: 1px solid #334155;">{c}</th>' for c in cells])
                html_lines.append(f"{th_cells}</tr></thead><tbody>")
            else:
                td_cells = "".join([f'<td style="padding: 9px 14px; border: 1px solid #e2e8f0; color: #334155; line-height: 1.5;">{c}</td>' for c in cells])
                html_lines.append(f'<tr style="background: #ffffff;">{td_cells}</tr>')
            continue
        else:
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False

        if not stripped:
            continue

        # Headings
        if stripped.startswith("## "):
            text = stripped[3:].strip()
            html_lines.append(
                f'<h2 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 26px 0 10px 0; padding-bottom: 6px; border-bottom: 2px solid #e2e8f0; letter-spacing: -0.01em;">'
                f'<span style="color: {theme["accent"]};">§</span> {text}'
                f'</h2>'
            )
        elif stripped.startswith("### "):
            text = stripped[4:].strip()
            html_lines.append(f'<h3 style="font-size: 15px; font-weight: 600; color: #1e293b; margin: 18px 0 6px 0;">{text}</h3>')
        elif stripped.startswith("#### "):
            text = stripped[5:].strip()
            html_lines.append(f'<h4 style="font-size: 14px; font-weight: 600; color: #475569; margin: 12px 0 4px 0;">{text}</h4>')
        # Bullet list
        elif stripped.startswith("- ") or stripped.startswith("* "):
            text = stripped[2:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'`(.*?)`', r'<code style="background: #f1f5f9; padding: 2px 5px; border-radius: 4px; font-family: monospace; color: #0f172a; font-size: 12px;">\1</code>', text)
            html_lines.append(f'<ul style="margin: 4px 0 6px 20px; line-height: 1.6;"><li style="color: #334155; margin-bottom: 4px;">{text}</li></ul>')
        # Numbered list
        elif re.match(r'^\d+\.\s+', stripped):
            text = re.sub(r'^\d+\.\s+', '', stripped)
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'`(.*?)`', r'<code style="background: #f1f5f9; padding: 2px 5px; border-radius: 4px; font-family: monospace; color: #0f172a; font-size: 12px;">\1</code>', text)
            html_lines.append(f'<ol style="margin: 4px 0 6px 20px; line-height: 1.6;"><li style="color: #334155; margin-bottom: 4px;">{text}</li></ol>')
        # Regular paragraph
        else:
            text = stripped
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            text = re.sub(r'`(.*?)`', r'<code style="background: #f1f5f9; padding: 2px 5px; border-radius: 4px; font-family: monospace; color: #0f172a; font-size: 12px;">\1</code>', text)
            html_lines.append(f'<p style="color: #334155; line-height: 1.65; margin: 8px 0;">{text}</p>')

    if in_table:
        html_lines.append("</tbody></table>")
    if in_code_block:
        code_content = "\n".join(code_block_lines)
        html_lines.append(f"<pre><code>{code_content}</code></pre>")

    # Footer callout
    html_lines.append(
        f'<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid {theme["accent"]}; padding: 12px 16px; border-radius: 6px; margin-top: 28px; font-size: 12px; color: #64748b;">'
        f'<strong>CloudOps Knowledge Engine</strong>: Synchronized with GCP Vertex AI Gemini agent. Changes reflected in real-time query reasoning.'
        f'</div>'
    )

    return "\n".join(html_lines)


async def seed_page(client: httpx.AsyncClient, base_url: str, space_key: str, auth: tuple, page: dict) -> dict:
    title = page["title"]
    ver = page.get("version", 1)
    formatted_html = markdown_to_confluence_storage_html(title, ver, page["content"])

    search_url = f"{base_url}/wiki/rest/api/content"
    search_params = {"title": title, "spaceKey": space_key, "expand": "version"}
    
    try:
        search_resp = await client.get(search_url, params=search_params, auth=auth)
        results = search_resp.json().get("results", []) if search_resp.status_code == 200 else []

        if results:
            existing = results[0]
            page_id = existing["id"]
            current_ver = existing.get("version", {}).get("number", 1)
            update_url = f"{base_url}/wiki/rest/api/content/{page_id}"
            update_payload = {
                "version": {"number": current_ver + 1},
                "title": title,
                "type": "page",
                "body": {
                    "storage": {
                        "value": formatted_html,
                        "representation": "storage"
                    }
                }
            }
            res = await client.put(update_url, json=update_payload, auth=auth)
            if res.status_code == 200:
                data = res.json()
                web_link = f"{base_url}/wiki{data.get('_links', {}).get('webui', '')}"
                print(f"  [OK] Updated (v{current_ver+1}): {title} -> {web_link}")
                return {"status": "updated", "id": page_id, "title": title, "url": web_link}
            else:
                print(f"  ! Update failed for {title}: {res.status_code} {res.text[:150]}")
                return {"status": "failed", "title": title}
        else:
            create_payload = {
                "type": "page",
                "title": title,
                "space": {"key": space_key},
                "body": {
                    "storage": {
                        "value": formatted_html,
                        "representation": "storage"
                    }
                }
            }
            res = await client.post(search_url, json=create_payload, auth=auth)
            if res.status_code in (200, 201):
                data = res.json()
                page_id = data.get("id")
                web_link = f"{base_url}/wiki{data.get('_links', {}).get('webui', '')}"
                print(f"  [OK] Created: {title} (ID: {page_id}) -> {web_link}")
                return {"status": "created", "id": page_id, "title": title, "url": web_link}
            else:
                print(f"  ! Creation failed for {title}: {res.status_code} {res.text[:150]}")
                return {"status": "failed", "title": title}
    except Exception as e:
        print(f"  ! Exception on {title}: {e}")
        return {"status": "error", "title": title}


async def main():
    base_url = os.getenv("CONFLUENCE_BASE_URL", "https://abhinavclouds.atlassian.net").rstrip("/")
    email = os.getenv("CONFLUENCE_USER_EMAIL", "abhinavclouds@gmail.com")
    token = os.getenv("CONFLUENCE_API_TOKEN")
    space_key = os.getenv("CONFLUENCE_SPACE_KEY", "AITEST")

    if not token:
        print("ERROR: CONFLUENCE_API_TOKEN is not set.")
        sys.exit(1)

    auth = (email, token)
    print("=" * 70)
    print("CloudOps AI Confluence Visual Seeder")
    print(f"Target Instance : {base_url}")
    print(f"Target Space    : {space_key}")
    print(f"User Email      : {email}")
    print(f"Total Pages     : {len(SEED_PAGES)}")
    print("=" * 70)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Atlassian-Token": "no-check",
    }

    async with httpx.AsyncClient(timeout=35.0, headers=headers) as client:
        space_url = f"{base_url}/wiki/rest/api/space/{space_key}"
        s_resp = await client.get(space_url, auth=auth)
        if s_resp.status_code == 200:
            print(f"[OK] Space '{space_key}' verified on Confluence Cloud.\n")
        else:
            print(f"! Space check returned {s_resp.status_code}. Proceeding...\n")

        success_count = 0
        created_pages = []
        for i, page in enumerate(SEED_PAGES, 1):
            print(f"[{i}/{len(SEED_PAGES)}] Publishing '{page['title']}'...")
            res = await seed_page(client, base_url, space_key, auth, page)
            if res.get("status") in ("created", "updated"):
                success_count += 1
                created_pages.append(res)
            await asyncio.sleep(0.35)

        print("\n" + "=" * 70)
        print(f"[DONE] Successfully published {success_count}/{len(SEED_PAGES)} rich pages to Confluence Cloud!")
        print(f"View all pages at: {base_url}/wiki/spaces/{space_key}/pages")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
