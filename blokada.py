# blokada_modes_commented.py
# --------------------------------
# Gra "Blokada" — deterministyczna gra logiczna dla 2 graczy.
# Ten plik zawiera: trzy tryby rozgrywki (PvP, PvAI, AvA) oraz
# bardzo szczegółowe komentarze w języku polskim, które wyjaśniają
# podejmowane decyzje projektowe i działanie każdego fragmentu kodu.
#
# ZASADY W SKRÓCIE
# -----------------
# * Plansza NxN (domyślnie 7x7).
# * Każdy z graczy ma jeden pionek; startują w przeciwległych rogach.
# * Tura gracza:
#     1) wykonaj ruch pionkiem o JEDNO pole w 8 kierunkach na PUSTE pole,
#     2) postaw blokadę (#) na dowolnym PUSTYM polu.
# * Pionków i blokad nie da się zdejmować ani nadpisywać.
# * Przegrywa ten gracz, który NA POCZĄTKU swojej tury nie ma legalnego ruchu.
#   (czyli jest "otoczony" blokadami / krawędzią / pionkiem przeciwnika).
#
# TRYBY
# -----
# * PvP  (Player vs Player) — dwóch ludzi przy klawiaturze.
# * PvAI (Player vs AI)     — człowiek przeciwko sztucznej inteligencji.
# * AvA  (AI vs AI)         — dwie SI grają przeciwko sobie (pokaz strategii).
#
# SZTUCZNA INTELIGENCJA (AI)
# --------------------------
# AI jest w pełni deterministyczna (brak losowości). Dla swojej tury:
# * rozważa wszystkie legalne ruchy pionkiem,
# * dla każdego ruchu rozważa sensowne pozycje blokad (zawężony zbiór kandydatów),
# * ocenia powstałą pozycję funkcją heurystyczną 'evaluate',
# * symuluje "chciwą" (greedy) jednoruchową odpowiedź przeciwnika,
# * wybiera parę (ruch, blokada), która maksymalizuje różnicę ocen.
#
# Heurystyka preferuje:
# * większą mobilność (liczbę ruchów) własną, mniejszą przeciwnika,
# * mniejszą odległość do przeciwnika (łatwiej go odcinać),
# * większą liczbę pustych pól w sąsiedztwie własnego pionka,
# * lekki bias w stronę środka planszy (często strategicznie korzystny).

from typing import List, Tuple, Optional

# ===== Parametry gry (łatwo zmienialne) =====
N = 7  # rozmiar planszy; zmień na 5 dla szybszych partii
EMPTY = "."  # puste pole na planszy
BLOCK = "#"  # zablokowane pole (nie można na nie wejść ani go zmienić)
P1 = "A"     # oznaczenie gracza 1 (zaczyna)
P2 = "B"     # oznaczenie gracza 2

# Pozycje startowe (przeciwległe rogi). Jeśli zmienisz N, starty
# automatycznie dostosują się do nowego rozmiaru planszy.
START_POS = {
    P1: (0, 0),              # lewy-górny róg (wiersz 0, kolumna 0)
    P2: (N - 1, N - 1),      # prawy-dolny róg
}

# ===== Funkcje pomocnicze ogólne =====
def in_bounds(r: int, c: int) -> bool:
    """Zwraca True, jeśli współrzędne (r, c) mieszczą się w granicach planszy."""
    return 0 <= r < N and 0 <= c < N

def neighbors8(r: int, c: int):
    """Generator wszystkich sąsiednich pól w 8 kierunkach (król w szachach).
    Nie zwraca pola (r, c) — tylko sąsiadów w promieniu 1.
    Filtruje pola wychodzące poza planszę.
    """
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc):
                yield rr, cc

def manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """Odległość Manhattan (|dx| + |dy|). Prosta i szybka metryka.
    W tej grze nie jest to idealna miara (bo ruchy są po skosie dozwolone),
    ale sprawdza się jako komponent heurystyki / preferencja zbliżania.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ===== Reprezentacja i logika gry =====
class Blokada:
    """Główna klasa reprezentująca stan gry (plansza, pionki, tura)."""

    def __init__(self):
        # Tworzymy pustą planszę NxN, wypełnioną kropkami.
        self.board: List[List[str]] = [[EMPTY for _ in range(N)] for _ in range(N)]

        # Pozycje pionków dwóch graczy.
        self.pos = {
            P1: START_POS[P1],
            P2: START_POS[P2],
        }

        # Umieszczamy pionki na planszy w pozycjach startowych.
        r1, c1 = self.pos[P1]
        r2, c2 = self.pos[P2]
        self.board[r1][c1] = P1
        self.board[r2][c2] = P2

        # Zaczyna gracz A.
        self.current = P1

    def clone(self) -> "Blokada":
        """Płytka kopia stanu gry; wykorzystywana przez AI do symulacji.
        Uwaga: kopiujemy struktury tak, by symulacje nie zmieniały oryginału.
        """
        g = Blokada.__new__(Blokada)  # pomijamy __init__ (będzie szybciej)
        g.board = [row[:] for row in self.board]  # kopia wierszy
        g.pos = dict(self.pos)                    # kopia pozycji pionków
        g.current = self.current                  # tura gracza
        return g

    def print_board(self):
        """Czytelny wydruk planszy z nagłówkami współrzędnych 1..N.
        Służy wyłącznie do interakcji konsolowej (debug / rozgrywka).
        """
        print("\n   " + " ".join(f"{c:>2}" for c in range(1, N + 1)))
        print("   " + "--" * N + "-")
        for i, row in enumerate(self.board, start=1):
            print(f"{i:>2}| " + " ".join(row))
        print()

    def legal_moves(self, player: str) -> List[Tuple[int, int]]:
        """Lista legalnych ruchów (puste sąsiednie pola w 8 kierunkach).
        Zwracamy listę krotek (r, c)."""
        r, c = self.pos[player]
        return [(rr, cc) for rr, cc in neighbors8(r, c) if self.board[rr][cc] == EMPTY]

    def legal_blocks(self) -> List[Tuple[int, int]]:
        """Lista wszystkich pustych pól, na których można postawić blokadę."""
        blocks = []
        for r in range(N):
            for c in range(N):
                if self.board[r][c] == EMPTY:
                    blocks.append((r, c))
        return blocks

    def move(self, player: str, dest: Tuple[int, int]) -> bool:
        """Próbuje wykonać ruch pionkiem gracza 'player' na pole 'dest'.
        Zwraca True, jeśli się udało; False, jeśli ruch był nielegalny.
        Warunki:
         * dest musi być w granicach planszy,
         * dest musi być puste,
         * dest musi leżeć w odległości 1 w 8-kącie (max(|dx|, |dy|) == 1).
        """
        r, c = self.pos[player]
        rr, cc = dest
        if not in_bounds(rr, cc) or self.board[rr][cc] != EMPTY:
            return False
        if max(abs(rr - r), abs(cc - c)) != 1:
            return False
        # Zdejmujemy pionek ze starego pola i kładziemy na nowym.
        self.board[r][c] = EMPTY
        self.board[rr][cc] = player
        self.pos[player] = (rr, cc)
        return True

    def place_block(self, rc: Tuple[int, int]) -> bool:
        """Próbuje postawić blokadę na pustym polu rc.
        Zwraca True, jeśli się udało; False w przeciwnym wypadku.
        """
        r, c = rc
        if not in_bounds(r, c) or self.board[r][c] != EMPTY:
            return False
        self.board[r][c] = BLOCK
        return True

    def has_moves(self, player: str) -> bool:
        """Czy gracz 'player' ma przynajmniej jeden legalny ruch?"""
        return len(self.legal_moves(player)) > 0

    def switch(self):
        """Zmiana tury: jeśli było A, teraz B; jeśli było B, teraz A."""
        self.current = P1 if self.current == P2 else P2

    def finished(self) -> Optional[str]:
        """Sprawdza, czy gra się zakończyła. Zwraca zwycięzcę ("A"/"B") lub None.
        Przypomnienie: przegrywa gracz, który NA POCZĄTKU swojej tury nie ma ruchu.
        """
        if not self.has_moves(self.current):
            # Aktualny gracz nie może wykonać ruchu -> przegrywa.
            return P1 if self.current == P2 else P2
        return None

# ===== Heurystyka i wybór ruchów dla AI =====
def evaluate(g: Blokada, player: str) -> int:
    """Ocena pozycji z perspektywy 'player'. Wyższe = lepsze.
    Składa się z kilku składników: mobilności, dystansu do przeciwnika,
    wolnej przestrzeni wokół pionków i lekkiej preferencji środka.
    Uwaga: funkcja jest celowo prosta i szybka (1-ply + greedy reply).
    """
    me = player
    opp = P1 if player == P2 else P2

    # 1) Mobilność: różnica w liczbie legalnych ruchów.
    my_moves = len(g.legal_moves(me))
    opp_moves = len(g.legal_moves(opp))
    mobility = 3 * (my_moves - opp_moves)  # waga 3 (doświadczalnie dobrana)

    # 2) Dystans do przeciwnika: im bliżej, tym łatwiej odciąć.
    d = manhattan(g.pos[me], g.pos[opp])
    dist_term = -d  # mniejsza odległość => większa ocena

    # 3) Wolna przestrzeń wokół pionków (lokalna swoboda).
    my_free = sum(1 for r, c in neighbors8(*g.pos[me]) if g.board[r][c] == EMPTY)
    opp_free = sum(1 for r, c in neighbors8(*g.pos[opp]) if g.board[r][c] == EMPTY)
    zone = 2 * (my_free - opp_free)  # waga 2

    # 4) Bias do środka (zwykle korzystniejszy teren).
    center = ((N - 1) / 2, (N - 1) / 2)
    center_bias = - (abs(g.pos[me][0] - center[0]) + abs(g.pos[me][1] - center[1])) * 0.5

    # Suma składników. Rzutujemy na int (wystarczy do porównań i stabilizuje porządek).
    return int(mobility + dist_term + zone + center_bias)

def candidate_blocks_for(g: Blokada, player_who_just_moved: str) -> List[Tuple[int, int]]:
    """Zwraca zawężoną (i posortowaną) listę sensownych pól na blokadę.
    Strategia: najpierw próbujemy zająć pola będące legalnymi ruchami przeciwnika
    (bezpośrednie odcięcie). Następnie dodajemy pola wokół przeciwnika oraz wokół
    aktualnego gracza (zacieśnianie "korytarzy"). Jeśli to wciąż za mało,
    bierzemy wszystkie puste pola. Posortowanie zapewnia determinizm.
    """
    opp = P1 if player_who_just_moved == P2 else P2
    cand = set()

    # a) Blokujemy bezpośrednio legalne ruchy przeciwnika.
    for sq in g.legal_moves(opp):
        cand.add(sq)

    # b) Jeśli mało, rozważ pola sąsiednie do pionka przeciwnika.
    for sq in neighbors8(*g.pos[opp]):
        if g.board[sq[0]][sq[1]] == EMPTY:
            cand.add(sq)

    # c) Dodatkowo pola sąsiednie do pionka gracza, który właśnie się ruszył.
    for sq in neighbors8(*g.pos[player_who_just_moved]):
        if g.board[sq[0]][sq[1]] == EMPTY:
            cand.add(sq)

    # d) Ostatecznie — jeśli nic nie znaleźliśmy — wszystkie puste pola.
    if not cand:
        for r in range(N):
            for c in range(N):
                if g.board[r][c] == EMPTY:
                    cand.add((r, c))

    # Zwracamy listę posortowaną, aby decyzje AI były w pełni powtarzalne.
    return sorted(list(cand))

def ai_choose_action(g: Blokada, player: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Wybór pary (ruch, blokada) dla AI grającej kolorem 'player'.
    Algorytm:
    * iterujemy po wszystkich legalnych ruchach (posortowanych dla determinizmu),
    * po każdym ruchu generujemy listę kandydackich blokad,
    * dla każdej (ruch, blokada) symulujemy stan i oceniamy go,
    * dodatkowo symulujemy jedną greedy-odpowiedź przeciwnika,
    * wybieramy najlepszą parę wg oceny evaluate po odejmowaniu reply_score.
    """
    opp = P1 if player == P2 else P2
    best_score = None
    best_pair = None

    legal_moves = g.legal_moves(player)
    legal_moves.sort()  # stała kolejność -> brak losowości

    for mv in legal_moves:
        g1 = g.clone()
        assert g1.move(player, mv)

        # Wyznaczamy sensowne kandydatury blokad po tym ruchu.
        blocks = candidate_blocks_for(g1, player)
        for bl in blocks:
            if g1.board[bl[0]][bl[1]] != EMPTY:
                continue
            g2 = g1.clone()
            assert g2.place_block(bl)

            # Symulujemy jedną greedy-odpowiedź przeciwnika (jego najlepszą parę).
            reply_score = simulate_greedy_reply(g2, opp, pov=player)

            # Własna ocena pozycji po (mv, bl) minus ocena przewidywanej odpowiedzi przeciwnika.
            score_now = evaluate(g2, player) - reply_score

            pair = (mv, bl)
            # kryterium wyboru: lepszy wynik, a przy remisie — porządek leksykograficzny
            if (best_score is None) or (score_now > best_score) or (score_now == best_score and pair < best_pair):
                best_score = score_now
                best_pair = pair

    # Jeśli z jakiegoś powodu nie znaleziono ruchów (nie powinno się zdarzyć, bo wcześniej to sprawdzamy)
    if best_pair is None:
        return ((-1, -1), (-1, -1))
    return best_pair

def simulate_greedy_reply(g: Blokada, reply_player: str, pov: str) -> int:
    """Symulacja JEDNEJ tury przeciwnika (reply_player).
    Wybiera dla siebie najlepszą parę (ruch, blokada) maksymalizując evaluate(g, pov)
    z punktu widzenia gracza 'pov' (naszej AI), co w praktyce odwzorowuje
    "najgorszy" dla nas realistyczny scenariusz w następnym ruchu.
    Zwraca ocenę pozycji po najlepszej odpowiedzi przeciwnika.
    """
    legal_moves = g.legal_moves(reply_player)
    if not legal_moves:
        # Przeciwnik nie ma odpowiedzi — zwracamy bieżącą ocenę
        return evaluate(g, pov)
    legal_moves.sort()

    best = None
    best_sc = None
    for mv in legal_moves:
        g1 = g.clone()
        if not g1.move(reply_player, mv):
            continue
        blocks = candidate_blocks_for(g1, reply_player)
        for bl in blocks:
            if g1.board[bl[0]][bl[1]] != EMPTY:
                continue
            g2 = g1.clone()
            if not g2.place_block(bl):
                continue
            sc = evaluate(g2, pov)
            pair = (mv, bl)
            if (best_sc is None) or (sc > best_sc) or (sc == best_sc and pair < best):
                best_sc = sc
                best = pair
    return best_sc if best_sc is not None else evaluate(g, pov)

# ===== Interakcja konsolowa (wejście użytkownika) =====
def ask_coord(prompt: str) -> Optional[Tuple[int, int]]:
    """Pobiera od użytkownika współrzędne w formacie: "wiersz kolumna" (1..N).
    Zwraca krotkę indeksów 0..N-1 lub None, gdy użytkownik wpisze 'q'.
    Zawiera "pancerną" walidację i komunikaty o błędach.
    """
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("q", "quit", "exit"):
            return None
        parts = raw.replace(",", " ").split()
        if len(parts) != 2:
            print("❗ Podaj dwie liczby: wiersz kolumna (np. 3 4) lub 'q' aby wyjść.")
            continue
        try:
            r, c = int(parts[0]), int(parts[1])
        except ValueError:
            print("❗ Użyj liczb całkowitych.")
            continue
        if not (1 <= r <= N and 1 <= c <= N):
            print(f"❗ Dozwolone współrzędne: 1..{N}.")
            continue
        return (r - 1, c - 1)

def choose_mode() -> str:
    """Proste menu wyboru trybu rozgrywki."""
    print("Wybierz tryb:")
    print("  1) Gracz vs Gracz (PvP)")
    print("  2) Gracz vs AI (PvAI)")
    print("  3) AI vs AI (AIvAI)")
    while True:
        m = input("Tryb [1/2/3]: ").strip()
        if m in ("1", "2", "3"):
            return m
        print("Wpisz 1, 2 albo 3.")

def choose_ai_side() -> str:
    """Dodatkowe menu: w trybie PvAI wybieramy, kto jest AI (A czy B)."""
    print("Kto ma być AI?")
    print("  1) AI gra jako A (zaczyna)")
    print("  2) AI gra jako B (drugi)")
    while True:
        s = input("Wybór [1/2]: ").strip()
        if s == "1":
            return P1
        if s == "2":
            return P2
        print("Wpisz 1 albo 2.")

# ===== Główne pętle rozgrywek =====
def loop_pvp():
    """Pętla gry dla dwóch ludzi (Player vs Player)."""
    game = Blokada()
    print("=== Gra 'Blokada' — PvP ===")
    print(f"Plansza: {N}x{N}. A start: (1,1), B start: ({N},{N}).")
    print("Tura: ruch pionkiem (1 pole, 8 kierunków) -> blokada '#'. 'q' aby wyjść.\n")
    game.print_board()

    while True:
        # Sprawdzamy, czy gra się zakończyła (ktoś zablokowany na starcie tury)
        winner = game.finished()
        if winner:
            print(f"🏆 Zwycięzca: {winner}")
            break

        player = game.current
        print(f"👉 Tura gracza {player}")
        if not game.has_moves(player):
            # Redundancja względem finished(), ale zostawiamy dla czytelności.
            print(f"❌ {player} nie ma ruchów.")
            game.switch()
            print(f"🏆 Zwycięzca: {game.current}")
            break

        # --- Faza ruchu pionkiem ---
        while True:
            mv = ask_coord("Ruch pionkiem (wiersz kolumna): ")
            if mv is None:
                print("👋 Przerwano.")
                return
            if game.move(player, mv):
                break
            print("❗ Niedozwolony ruch (1 pole, puste).")

        game.print_board()

        # --- Faza stawiania blokady ---
        while True:
            bl = ask_coord("Postaw blokadę '#'(wiersz kolumna): ")
            if bl is None:
                print("👋 Przerwano.")
                return
            if game.place_block(bl):
                break
            print("❗ Nie można postawić blokady tutaj.")

        game.print_board()
        game.switch()

def loop_pvai(ai_side: str):
    """Pętla gry człowiek vs AI. 'ai_side' określa, który gracz jest sterowany przez SI."""
    game = Blokada()
    print("=== Gra 'Blokada' — PvAI ===")
    print(f"AI gra jako: {ai_side}. Plansza {N}x{N}. 'q' aby wyjść.\n")
    game.print_board()

    while True:
        winner = game.finished()
        if winner:
            print(f"🏆 Zwycięzca: {winner}")
            break

        player = game.current
        if not game.has_moves(player):
            print(f"❌ {player} nie ma ruchów.")
            game.switch()
            print(f"🏆 Zwycięzca: {game.current}")
            break

        if player == ai_side:
            # --- Tura AI ---
            mv, bl = ai_choose_action(game, player)
            print(f"🤖 {player} ruch -> {mv[0]+1} {mv[1]+1}, blokada -> {bl[0]+1} {bl[1]+1}")
            game.move(player, mv)
            game.place_block(bl)
            game.print_board()
            game.switch()
        else:
            # --- Tura człowieka ---
            print(f"👉 Twoja tura ({player})")
            while True:
                mv = ask_coord("Ruch pionkiem (wiersz kolumna): ")
                if mv is None:
                    print("👋 Przerwano.")
                    return
                if game.move(player, mv):
                    break
                print("❗ Niedozwolony ruch.")
            game.print_board()
            while True:
                bl = ask_coord("Postaw blokadę '#'(wiersz kolumna): ")
                if bl is None:
                    print("👋 Przerwano.")
                    return
                if game.place_block(bl):
                    break
                print("❗ Nie można postawić blokady tutaj.")
            game.print_board()
            game.switch()

def loop_ava(max_turns: int = 500):
    """Pętla gry AI vs AI. Parametr 'max_turns' zabezpiecza przed nieskończoną pętlą
    (np. w sytuacjach patowych)."""
    game = Blokada()
    print("=== Gra 'Blokada' — AI vs AI ===")
    game.print_board()
    turns = 0
    while turns < max_turns:
        winner = game.finished()
        if winner:
            print(f"🏆 Zwycięzca: {winner}")
            break

        player = game.current
        if not game.has_moves(player):
            print(f"❌ {player} nie ma ruchów.")
            game.switch()
            print(f"🏆 Zwycięzca: {game.current}")
            break

        mv, bl = ai_choose_action(game, player)
        print(f"🤖 {player} ruch -> {mv[0]+1} {mv[1]+1}, blokada -> {bl[0]+1} {bl[1]+1}")
        game.move(player, mv)
        game.place_block(bl)
        game.print_board()
        game.switch()
        turns += 1
    else:
        print("⏱️ Limit tur osiągnięty (remis techniczny).")

# ===== Wejście w program =====
def main():
    mode = choose_mode()
    if mode == "1":
        loop_pvp()
    elif mode == "2":
        ai_side = choose_ai_side()
        loop_pvai(ai_side)
    else:
        loop_ava()

if __name__ == "__main__":
    main()
