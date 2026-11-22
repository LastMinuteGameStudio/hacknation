"""TuAED: dane testowe lokalnego portalu (portal/URUCHOMIENIE-TUAED.md).

Tworzy (idempotentnie, po e-mailu / tytule):
- superusera `admin@tuaed.local`,
- dwie instytucje dostawców AED z kontami redaktorów,
- w każdej zbiór „Defibrylatory AED …” z zasobem-linkiem do pliku z TuAED (CSV v0.5)
  i włączoną „Aktualizacją automatyczną” (codziennie, bez końca).

Uruchomienie (po init_mcod_db):
    docker compose -f docker-compose.local.yml -f docker-compose.tuaed.yml run --rm mcod-local-run \
        python manage.py shell -c "from mcod.tuaed_dane_testowe import main; main()"

Adresy plików można podmienić zmiennymi TUAED_URL_1 i TUAED_URL_2.
Zapis zasobu ze statusem `published` sam uruchamia pobranie linku (sygnał revalidate_resource →
entrypoint_process_resource_validation_task) i harmonogram aktualizacji (Resource.schedule_data_date_update).
"""

from __future__ import annotations

import datetime
import os

from django.db import transaction

HASLO = "TuAED-test-2026!"  # tylko lokalne demo, nie używać nigdzie indziej

DOSTAWCY = [
    {
        "instytucja": "Urząd Miejski w Przemyślu (test TuAED)",
        "slug": "um-przemysl-test-tuaed",
        "email_instytucji": "aed@przemysl.test",
        "miasto": "Przemyśl",
        "redaktor": "redaktor.przemysl@tuaed.local",
        "imie_nazwisko": "Redaktor Przemyśl",
        "zbior": "Defibrylatory AED w Przemyślu",
        "url": os.environ.get("TUAED_URL_1", "https://tuaed.wkrynski.dev/d/kznsks42.csv"),
    },
    {
        "instytucja": "Urząd Miasta Krosna (test TuAED)",
        "slug": "um-krosno-test-tuaed",
        "email_instytucji": "aed@krosno.test",
        "miasto": "Krosno",
        "redaktor": "redaktor.krosno@tuaed.local",
        "imie_nazwisko": "Redaktor Krosno",
        "zbior": "Defibrylatory AED w Krośnie",
        "url": os.environ.get("TUAED_URL_2", "https://tuaed.wkrynski.dev/d/qy7g6px5.csv"),
    },
]

OPIS_ZBIORU = (
    "Wykaz automatycznych defibrylatorów zewnętrznych (AED) w formacie wzorcowego zakresu danych v0.5. "
    "Plik przygotowany w TuAED i aktualizowany automatycznie z adresu dostawcy. Dane testowe."
)


def _uzytkownik(User, email: str, fullname: str, **pola):
    u = User.objects.filter(email=email).first()
    if u is None:
        u = User(email=email)
    u.fullname = fullname
    u.state = "active"
    for k, v in pola.items():
        setattr(u, k, v)
    u.set_password(HASLO)  # z pominięciem walidatorów siły hasła (to konto testowe)
    u.save()
    return u


def _kategoria(Category):
    kat = Category.objects.filter(code="HEAL").first()
    if kat is None:
        kat = Category.objects.create(code="HEAL", title="Zdrowie", description="Zdrowie")
    return kat


@transaction.atomic
def main() -> None:
    from mcod.categories.models import Category
    from mcod.datasets.models import Dataset
    from mcod.organizations.models import Organization
    from mcod.resources.models import Resource
    from mcod.users.models import User

    _uzytkownik(User, "admin@tuaed.local", "Administrator TuAED", is_staff=True, is_superuser=True)
    kategoria = _kategoria(Category)
    dzis = datetime.date.today()

    for d in DOSTAWCY:
        org = Organization.objects.filter(title=d["instytucja"]).first() or Organization(title=d["instytucja"])
        org.slug = d["slug"]
        org.institution_type = Organization.INSTITUTION_TYPE_LOCAL
        org.email = d["email_instytucji"]
        org.city = d["miasto"]
        org.status = "published"
        org.save()

        redaktor = _uzytkownik(User, d["redaktor"], d["imie_nazwisko"], is_staff=True, is_superuser=False)
        redaktor.organizations.add(org)

        ds = Dataset.objects.filter(title=d["zbior"], organization=org).first() or Dataset(title=d["zbior"], organization=org)
        ds.notes = OPIS_ZBIORU
        ds.update_frequency = "daily"
        ds.has_dynamic_data = False
        ds.has_high_value_data = False
        ds.has_research_data = False
        ds.status = "published"
        ds.save()
        ds.categories.add(kategoria)

        res = Resource.objects.filter(dataset=ds, title=f"{d['zbior']} (CSV)").first()
        if res is None:
            res = Resource(dataset=ds, title=f"{d['zbior']} (CSV)")
        res.description = "Plik CSV (RFC 4180, UTF-8) zgodny z zakresem v0.5, publikowany przez TuAED."
        res.link = d["url"]
        res.type = "file"
        res.format = "csv"
        res.has_dynamic_data = False
        res.has_high_value_data = False
        res.has_research_data = False
        res.data_date = dzis
        res.is_auto_data_date = True  # „Aktualizacja automatyczna” w panelu
        res.data_date_update_period = "daily"
        res.automatic_data_date_start = dzis
        res.endless_data_date_update = True
        res.status = "published"
        res.save()

        print(f"{org.title}: redaktor {redaktor.email}, zbiór #{ds.pk}, zasób #{res.pk} → {res.link}")

    print(f"Superuser: admin@tuaed.local. Hasło wszystkich kont testowych: {HASLO}")
