
import os, json, time, argparse, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_projects(index_url="https://arpa-e.energy.gov/programs-and-initiatives/search-all-projects", max_pages=10, delay=0.5):
    # Many results are rendered server-side; we can paginate by "page" param if supported, else single page.
    projects = []
    for p in range(1, max_pages+1):
        url = index_url
        if p > 1:
            # Heuristic: try a common pagination param
            url = f"{index_url}?page={p-1}"
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            break
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("article, .views-row, .node--type-project, .card")
        found = 0
        for c in cards:
            title = (c.get_text(" ", strip=True) or "").strip()
            link = None
            a = c.find("a")
            if a and a.get("href"):
                link = urljoin(index_url, a.get("href"))
            # Keep only plausible records with a link
            if link and title:
                projects.append({"title": title, "url": link})
                found += 1
        if found == 0 and p > 2:
            break
        time.sleep(delay)
    # dedupe by url
    seen = set()
    uniq = []
    for r in projects:
        if r["url"] in seen: continue
        seen.add(r["url"])
        uniq.append(r)
    return uniq

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index_url", default="https://arpa-e.energy.gov/programs-and-initiatives/search-all-projects")
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--max_pages", type=int, default=10)
    args = ap.parse_args()
    data = scrape_projects(args.index_url, max_pages=args.max_pages)
    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump({"items": data}, f, indent=2)

if __name__ == "__main__":
    main()
