from datetime import datetime
import json
import re
from bs4 import BeautifulSoup
import requests

# КАТАЛОГ С ЛИНКОВЕ И СЕЛЕКТОРИ ЗА БОРСИТЕ
PRODUCT_SOURCES = {
    "GK_STD_12.5": {
        "Баущоф + Метал": {
            "url": "https://www.baustoff-metall.bg/knauf-standarten-gipsokarton-gkb-a13-12-5-1200-2000mm/",
            "selectors": [
                ".price--content",
                ".product--price",
                "[itemprop='price']",
                ".price",
            ],
        },
        "Топливо": {
            "url": "https://toplivo.bg/produkt/gipsokarton-knauf-a13-gkb-12-5-1200-2000",
            "selectors": [
                ".product-price",
                ".special-price .price",
                ".price",
                "[itemprop='price']",
            ],
        },
        "Ташев-Галвинг": {
            "url": "https://www.tashev-galving.com/bg/articul/404810/gipsokarton-knauf-tip-a-12-5x1200x2000-mm",
            "selectors": [
                ".price-new",
                ".product-price",
                "[itemprop='price']",
                ".price",
            ],
        },
    },
    "GK_STD_9.5": {
        "Баущоф + Метал": {
            "url": "https://www.baustoff-metall.bg/knauf-standarten-gipsokarton-gkb-a10-9-5-1200-2000mm/",
            "selectors": [
                ".price--content",
                ".product--price",
                "[itemprop='price']",
                ".price",
            ],
        },
        "Топливо": {
            "url": (
                "https://toplivo.bg/produkt/gipsokarton-knauf-a10-9-5-1200-2000"
            ),
            "selectors": [".product-price", ".price", "[itemprop='price']"],
        },
        "Ташев-Галвинг": {
            "url": "https://www.tashev-galving.com/bg/articul/404809/gipsokarton-knauf-tip-a-9-5x1200x2000-mm",
            "selectors": [
                ".price-new",
                ".product-price",
                "[itemprop='price']",
                ".price",
            ],
        },
    },
    "GK_VLAG_12.5": {
        "Баущоф + Метал": {
            "url": "https://www.baustoff-metall.bg/knauf-vlagoustoychiv-gipsokarton-gkbi-h13-12-5-1200-2000mm/",
            "selectors": [
                ".price--content",
                ".product--price",
                "[itemprop='price']",
                ".price",
            ],
        },
        "Топливо": {
            "url": "https://toplivo.bg/produkt/gipsokarton-vlagoustoychiv-knauf-h13-gkbi-12-5-1200-2000",
            "selectors": [".product-price", ".price", "[itemprop='price']"],
        },
        "Ташев-Галвинг": {
            "url": "https://www.tashev-galving.com/bg/articul/404813/gipsokarton-vlagoustoychiv-knauf-tip-h2-12-5x1200x2000-mm",
            "selectors": [
                ".price-new",
                ".product-price",
                "[itemprop='price']",
                ".price",
            ],
        },
    },
    "PROF_CD_60": {
        "Баущоф + Метал": {
            "url": "https://www.baustoff-metall.bg/profil-cd-60-27-3000mm/",
            "selectors": [".price--content", "[itemprop='price']", ".price"],
        },
        "Топливо": {
            "url": "https://toplivo.bg/produkt/profil-cd-60-27-3m",
            "selectors": [".product-price", ".price", "[itemprop='price']"],
        },
        "Ташев-Галвинг": {
            "url": "https://www.tashev-galving.com/bg/articul/601105/profil-za-gipsokarton-cd-60-27-3000-mm",
            "selectors": [
                ".price-new",
                ".product-price",
                "[itemprop='price']",
                ".price",
            ],
        },
    },
    "PROF_UD_28": {
        "Баущоф + Метал": {
            "url": "https://www.baustoff-metall.bg/profil-ud-28-27-3000mm/",
            "selectors": [".price--content", "[itemprop='price']", ".price"],
        },
        "Топливо": {
            "url": "https://toplivo.bg/produkt/profil-ud-28-27-3m",
            "selectors": [".product-price", ".price", "[itemprop='price']"],
        },
        "Ташев-Галвинг": {
            "url": "https://www.tashev-galving.com/bg/articul/601106/profil-za-gipsokarton-ud-28-27-3000-mm",
            "selectors": [
                ".price-new",
                ".product-price",
                "[itemprop='price']",
                ".price",
            ],
        },
    },
}


def extract_price(url, selectors):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "bg-BG,bg;q=0.9,en;q=0.8",
    }
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code != 200:
            print(f"⚠️ Статус {r.status_code} за: {url}")
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # 1. Проверка за мета таг с цена (schema.org / OpenGraph)
        meta_price = soup.find("meta", {"property": "product:price:amount"})
        if not meta_price:
            meta_price = soup.find("meta", {"itemprop": "price"})

        if meta_price and meta_price.get("content"):
            try:
                return round(
                    float(meta_price["content"].replace(",", ".")), 2
                )
            except ValueError:
                pass

        # 2. Проверка по CSS селектори
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                if el.has_attr("content"):
                    try:
                        return round(float(el["content"].replace(",", ".")), 2)
                    except ValueError:
                        pass

                text = el.get_text(strip=True).replace(",", ".")
                text = re.sub(r"(?<=\d)\s+(?=\d)", "", text)
                match = re.search(r"\d+\.\d+|\d+", text)
                if match:
                    price_val = float(match.group(0))
                    if price_val > 0:
                        return round(price_val, 2)

    except Exception as e:
        print(f"❌ Грешка при {url}: {e}")

    return None


def update_catalog():
    with open("prices.json", "r", encoding="utf-8") as f:
        catalog = json.load(f)

    updated_count = 0

    for item in catalog:
        item_id = item["id"]
        if item_id in PRODUCT_SOURCES:
            for store, info in PRODUCT_SOURCES[item_id].items():
                new_price = extract_price(info["url"], info["selectors"])
                if new_price is not None:
                    old_price = item["prices"].get(store)
                    item["prices"][store] = new_price
                    updated_count += 1
                    print(
                        f"✅ [{item_id}] {store}: {old_price} -> {new_price} €"
                    )
                else:
                    print(
                        f"ℹ️ [{item_id}] {store}: Запазена стара цена"
                        f" ({item['prices'].get(store)} €)"
                    )

        item["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"\nГотово! Обновени са {updated_count} позиции.")


if __name__ == "__main__":
    update_catalog()
