#  Blokada — deterministyczna gra logiczna w Pythonie

## 📘 Opis projektu

**Blokada** to prosta, strategiczna gra planszowa dla dwóch graczy — całkowicie **pozbawiona losowości**. Wynik każdej partii zależy wyłącznie od decyzji graczy. Gra może być rozgrywana w trzech trybach:

* 👥 **Gracz vs Gracz (PvP)** — dwóch graczy przy jednym komputerze.
* 🧠 **Gracz vs AI (PvAI)** — człowiek przeciwko sztucznej inteligencji.
* 🤖 **AI vs AI (AIvAI)** — dwie SI grają przeciwko sobie, umożliwiając obserwację strategii.

Gra rozgrywana jest w konsoli i nie wymaga żadnych zewnętrznych bibliotek.

---

## 🎯 Zasady gry

* Plansza ma rozmiar domyślnie **7×7 pól** (można to łatwo zmienić w kodzie).
* Każdy gracz ma **jeden pionek**:

  * Gracz **A** zaczyna w lewym górnym rogu.
  * Gracz **B** zaczyna w prawym dolnym rogu.
* Tura gracza składa się z dwóch kroków:

  1. **Ruch pionkiem** o jedno pole w dowolnym z 8 kierunków (jak król w szachach) na puste pole.
  2. **Postawienie blokady (#)** na dowolnym pustym polu planszy.
* Pionków i blokad nie można przesuwać ani usuwać.
* **Przegrywa gracz**, który **na początku swojej tury nie ma żadnego legalnego ruchu** (został całkowicie zablokowany).

---

## 🧠 Sztuczna inteligencja (AI)

AI w grze **nie korzysta z losowości** — jej decyzje są w pełni deterministyczne, co oznacza, że każda taka sama sytuacja prowadzi do identycznego ruchu.

### Heurystyka decyzji AI:

* Maksymalizuje swoją **mobilność** (liczbę możliwych ruchów).
* Minimalizuje **mobilność przeciwnika**.
* Preferuje **mniejszy dystans** do przeciwnika (łatwiej go odciąć).
* Wybiera pola, które **ograniczają ruchy przeciwnika** (blokuje jego możliwe ścieżki).
* Lekko preferuje **środkową część planszy** (zazwyczaj bardziej strategiczną).

### Tryb AI vs AI:

Pozwala zaobserwować, jak dwie identyczne SI rozgrywają między sobą partię w sposób w pełni deterministyczny.

---

## ⚙️ Instalacja i uruchomienie

### 1. Skopiuj repozytorium lub plik

```bash
git clone https://github.com/uzytkownik/blokada.git
cd blokada
```

Lub zapisz lokalnie plik `blokada_modes_commented.py`.

### 2. Uruchom grę

```bash
python blokada_modes_commented.py
```

### 3. Wybierz tryb gry z menu

```
Wybierz tryb:
  1) Gracz vs Gracz (PvP)
  2) Gracz vs AI (PvAI)
  3) AI vs AI (AvA)
```

---

## 🎮 Sterowanie

* Podczas tury gracza podaj współrzędne pola w formacie:

  ```
  wiersz kolumna
  ```

  np. `3 5` oznacza ruch lub blokadę w wierszu 3, kolumnie 5.
* Wpisz `q`, aby zakończyć grę.

---

## 🧩 Przykładowy przebieg tury

```
👉 Tura gracza A
Ruch pionkiem (wiersz kolumna): 2 2
Postaw blokadę '#'(wiersz kolumna): 3 3
```

Plansza po ruchu:

```
   1  2  3  4  5  6  7
   -------------------
 1| . . . . . . .
 2| . A . . . . .
 3| . . # . . . .
 4| . . . . . . .
 5| . . . . . . .
 6| . . . . . . .
 7| . . . . . . B
```

---

## 👨‍💻 Autorzy

s28838, s22775.

---
