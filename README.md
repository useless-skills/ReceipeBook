# Recipe & shopping list

## Layout
- `index.html`   public viewer (host on GitHub Pages)
- `data/*.json`  the "databases": units, categories, ingredients, recipes
- `images/`      recipe pictures
- `admin.html` + `server.py`  local editor (do NOT publish these)

## Edit data (local)
    python server.py        # opens http://localhost:8000/admin.html
Python 3 only, no packages needed. Changes are written straight to `data/*.json`.

## Publish
Commit and push, then enable Pages (Settings > Pages > branch `main`, folder `/root`).
Open `https://<user>.github.io/<repo>/` on your phone. After editing, push again.
To keep admin files out of the repo, add `admin.html` and `server.py` to `.gitignore`.

## Data model
- units: id, name, abbr
- categories: id, name, order (sorts the shopping list)
- ingredients: id, name, unit_id, category_id
- recipes: id, title, image, servings, ingredients[{ingredient_id, quantity}], steps[]
Quantities are stored for the recipe's base servings. Viewer scales with q * wanted / base (no rounding, shown with up to 2 decimals), then sums per ingredient across meals.
