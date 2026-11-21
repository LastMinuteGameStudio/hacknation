# Instrukcje dla agentów (Claude Code)

Na tym komputerze równolegle pracuje kilka sesji Claude, każda we własnym klonie repo.

## Komunikacja między agentami

1. **Wspólna tablica:** `~/Desktop/hacknation-wspolne/TABLICA.md` (poza repo, nie commitować).
   - Na starcie sesji i przed każdym researchem przeczytaj ostatnie wpisy.
   - Wyniki researchu, ustalenia i pytania do innych **dopisuj na końcu** zgodnie z zasadami w nagłówku pliku.
2. **Wiadomości bezpośrednie:** `ListAgents` pokazuje inne sesje na tym komputerze, a `SendMessage` wysyła do nich wiadomość. Używaj tego do pilnych rzeczy, a ustalenia i tak zapisuj na tablicy.

## Zasady repo

- Pracuj tylko we własnym klonie.
- Przed pushem zawsze `git pull --rebase`. Pushuj tylko na prośbę swojego użytkownika.
- Opisy zadań w `zadania/` zawierają wyłącznie fakty od organizatorów, bez proponowania rozwiązań. Każdy rodzaj treści ma osobny plik. W `zadania/06-mc-misja-aed/` są: `NOTATKI-ZESPOLU.md` (wnioski ludzi, z podpisem), `RESEARCH.md` (wyniki researchu), `ZRODLA-DANYCH.md`, `PYTANIA-DO-ORGANIZATORA.md` (sekcje podpisane autorem), `CHECKLISTA.md`. `zadania/WNIOSKI.md` dotyczy tylko wyboru zadania.
