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
- Opisy zadań w `zadania/` zawierają wyłącznie fakty od organizatorów, bez proponowania rozwiązań. Wnioski zespołu trafiają do `zadania/WNIOSKI.md`.
