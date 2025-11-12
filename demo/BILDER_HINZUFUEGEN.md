# 📸 Bilder hinzufügen

## Du musst jetzt 2 Bilder in den `demo/images/` Ordner kopieren:

### 1. Logo (logo.png)
- Das "the aigency" Logo (Bild 1)
- Speichern als: `demo/images/logo.png`
- Empfohlene Größe: 200x50px (wird auf 50px Höhe skaliert)

### 2. Hero Background (hero-bg.jpg)
- Das Office-Bild mit der Frau (Bild 2)
- Speichern als: `demo/images/hero-bg.jpg`
- Empfohlene Größe: 1920x1080px (Full HD)

---

## So fügst du die Bilder hinzu:

### Option A: Manuell kopieren
```bash
# 1. Speichere beide Bilder auf deinem Desktop
# 2. Kopiere sie in den Ordner:
cp ~/Desktop/logo.png demo/images/logo.png
cp ~/Desktop/hero-bg.jpg demo/images/hero-bg.jpg
```

### Option B: Im Finder
1. Öffne Finder
2. Gehe zu: `phone-agent-api/demo/images/`
3. Kopiere beide Bilder dort rein
4. Benenne sie um:
   - Logo → `logo.png`
   - Office-Bild → `hero-bg.jpg`

---

## Dann committen & pushen:

```bash
# Im phone-agent-api Ordner:
git checkout gh-pages
git add demo/
git commit -m "Update: Add logo and hero background image"
git push origin gh-pages
```

---

## Fertig! 🎉

Nach dem Push (1-2 Minuten warten) ist die Seite aktualisiert:
https://theaigency-ch.github.io/phone-agent-api/demo/
