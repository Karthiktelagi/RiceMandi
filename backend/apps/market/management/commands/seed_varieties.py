"""
Seed the database with real-world rice varieties commonly traded at APMC yards.
Run: python manage.py seed_varieties
"""
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from apps.market.models import Variety


VARIETIES = [
    # Premium Basmati
    {"name": "Basmati 370", "category": "rice", "grade": "grade_1", "description": "Premium long-grain aromatic basmati rice"},
    {"name": "Pusa Basmati 1121", "category": "rice", "grade": "grade_1", "description": "Extra-long grain basmati, world's longest rice grain"},
    {"name": "Pusa Basmati 1509", "category": "rice", "grade": "grade_1", "description": "Early-maturing basmati with extra-long grains"},
    {"name": "Sharbati", "category": "rice", "grade": "grade_1", "description": "Aromatic long-grain rice, basmati alternative"},
    {"name": "Dehraduni Basmati", "category": "rice", "grade": "grade_1", "description": "Traditional aromatic basmati from Dehradun"},

    # Medium Grain Popular
    {"name": "Sona Masuri", "category": "rice", "grade": "grade_2", "description": "Most popular medium-slender rice in South India"},
    {"name": "BPT 5204", "category": "rice", "grade": "grade_2", "description": "Sona Masuri type, high-yielding medium grain"},
    {"name": "MTU 1010", "category": "rice", "grade": "grade_2", "description": "Ponni type, widely grown in Andhra/Telangana"},
    {"name": "Ponni", "category": "rice", "grade": "grade_2", "description": "Popular medium-grain rice from Tamil Nadu"},
    {"name": "Swarna", "category": "rice", "grade": "grade_2", "description": "High-yielding long-grain rice, IRRI variety"},
    {"name": "HMT", "category": "rice", "grade": "grade_2", "description": "Karnataka's own high-yielding variety"},
    {"name": "Jaya", "category": "rice", "grade": "grade_2", "description": "High-yielding long-grain variety"},
    {"name": "Ratna", "category": "rice", "grade": "grade_2", "description": "Long-grain aromatic rice variety"},

    # Short Grain / Aromatic
    {"name": "Samba", "category": "rice", "grade": "grade_1", "description": "Premium short-grain aromatic rice, Tamil Nadu specialty"},
    {"name": "Jeera Samba", "category": "rice", "grade": "grade_1", "description": "Short-grain aromatic rice, cumin-like grains"},
    {"name": "Kasthuri", "category": "rice", "grade": "grade_1", "description": "Aromatic short-grain premium rice"},

    # Long Grain Non-Basmati
    {"name": "Parmal", "category": "rice", "grade": "grade_2", "description": "Long-grain non-basmati rice"},
    {"name": "PR-106", "category": "rice", "grade": "grade_2", "description": "Long-grain variety from Punjab"},
    {"name": "PR-113", "category": "rice", "grade": "grade_2", "description": "High-yielding long-grain variety"},
    {"name": "CSR-30", "category": "rice", "grade": "grade_2", "description": "Salt-tolerant long-grain variety"},
    {"name": "CR-1009", "category": "rice", "grade": "grade_2", "description": "High-yielding long-grain variety from Odisha"},
    {"name": "GNV-1089", "category": "rice", "grade": "grade_2", "description": "Karnataka high-yielding variety"},

    # Regional Varieties
    {"name": "ADT-36", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu Agricultural University variety"},
    {"name": "ADT-37", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu high-yielding variety"},
    {"name": "ADT-38", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu popular variety"},
    {"name": "ADT-39", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu high-yielding variety"},
    {"name": "ADT-43", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu popular variety"},
    {"name": "ADT-45", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu high-yielding variety"},
    {"name": "CO-43", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu Coimbatore variety"},
    {"name": "CO-47", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu Coimbatore variety"},
    {"name": "CO-50", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu Coimbatore variety"},
    {"name": "TKM-9", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu high-yielding variety"},
    {"name": "TKM-13", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu high-yielding variety"},
    {"name": "ASD-16", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu short-duration variety"},
    {"name": "ASD-18", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu popular variety"},
    {"name": "ASD-19", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu high-yielding variety"},
    {"name": "ASD-20", "category": "rice", "grade": "grade_2", "description": "Tamil Nadu popular variety"},

    # Paddy
    {"name": "Sona Masuri Paddy", "category": "paddy", "grade": "grade_2", "description": "Paddy form of Sona Masuri"},
    {"name": "Ponni Paddy", "category": "paddy", "grade": "grade_2", "description": "Paddy form of Ponni"},
    {"name": "Swarna Paddy", "category": "paddy", "grade": "grade_2", "description": "Paddy form of Swarna"},
    {"name": "HMT Paddy", "category": "paddy", "grade": "grade_2", "description": "Paddy form of HMT"},
    {"name": "Jaya Paddy", "category": "paddy", "grade": "grade_2", "description": "Paddy form of Jaya"},
    {"name": "BPT 5204 Paddy", "category": "paddy", "grade": "grade_2", "description": "Paddy form of BPT 5204"},
    {"name": "MTU 1010 Paddy", "category": "paddy", "grade": "grade_2", "description": "Paddy form of MTU 1010"},
    {"name": "Samba Paddy", "category": "paddy", "grade": "grade_1", "description": "Paddy form of Samba"},
    {"name": "Jeera Samba Paddy", "category": "paddy", "grade": "grade_1", "description": "Paddy form of Jeera Samba"},

    # Broken
    {"name": "Sona Masuri Broken", "category": "broken", "grade": "common", "description": "Broken Sona Masuri for industrial use"},
    {"name": "Swarna Broken", "category": "broken", "grade": "common", "description": "Broken Swarna for industrial use"},
    {"name": "Ponni Broken", "category": "broken", "grade": "common", "description": "Broken Ponni for industrial use"},

    # Bran
    {"name": "Rice Bran", "category": "bran", "grade": "common", "description": "Rice bran for oil extraction and feed"},
]


class Command(BaseCommand):
    help = _("Seed the database with real-world rice varieties.")

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for v in VARIETIES:
            variety, created = Variety.objects.get_or_create(
                name=v["name"],
                defaults={
                    "category": v["category"],
                    "grade": v["grade"],
                    "description": v["description"],
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {v['name']}"))
            else:
                skipped_count += 1
                self.stdout.write(f"  Skipped (exists): {v['name']}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Created {created_count} varieties, skipped {skipped_count} existing."
            )
        )
