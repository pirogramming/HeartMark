import os

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the local Site and social login apps from environment variables."

    def handle(self, *args, **options):
        site_domain = os.environ.get("SITE_DOMAIN", "127.0.0.1:8000")
        site_name = os.environ.get("SITE_NAME", site_domain)
        google_client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
        google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
        naver_client_id = os.environ.get("NAVER_CLIENT_ID", "").strip()
        naver_client_secret = os.environ.get("NAVER_CLIENT_SECRET", "").strip()
        kakao_client_id = os.environ.get("KAKAO_CLIENT_ID", "").strip()
        kakao_client_secret = os.environ.get("KAKAO_CLIENT_SECRET", "").strip()

        if not google_client_id or not google_client_secret:
            raise CommandError(
                "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required. "
                "Create .env from .env.example and fill them in."
            )
        if bool(naver_client_id) != bool(naver_client_secret):
            raise CommandError("NAVER_CLIENT_ID and NAVER_CLIENT_SECRET must be filled in together.")
        if bool(kakao_client_id) != bool(kakao_client_secret):
            raise CommandError("KAKAO_CLIENT_ID and KAKAO_CLIENT_SECRET must be filled in together.")

        site, _ = Site.objects.update_or_create(
            id=settings.SITE_ID,
            defaults={"domain": site_domain, "name": site_name},
        )

        self.configure_social_app(
            provider="google",
            name="Google",
            client_id=google_client_id,
            client_secret=google_client_secret,
            site=site,
        )

        if naver_client_id and naver_client_secret:
            self.configure_social_app(
                provider="naver",
                name="Naver",
                client_id=naver_client_id,
                client_secret=naver_client_secret,
                site=site,
            )

        if kakao_client_id and kakao_client_secret:
            self.configure_social_app(
                provider="kakao",
                name="Kakao",
                client_id=kakao_client_id,
                client_secret=kakao_client_secret,
                site=site,
            )

        self.stdout.write(self.style.SUCCESS(f"Configured Site: {site.domain}"))
        self.stdout.write(self.style.SUCCESS("Configured Google social login app."))
        if naver_client_id and naver_client_secret:
            self.stdout.write(self.style.SUCCESS("Configured Naver social login app."))
        if kakao_client_id and kakao_client_secret:
            self.stdout.write(self.style.SUCCESS("Configured Kakao social login app."))

    def configure_social_app(self, provider, name, client_id, client_secret, site):
        social_app, _ = SocialApp.objects.update_or_create(
            provider=provider,
            name=name,
            defaults={
                "client_id": client_id,
                "secret": client_secret,
            },
        )
        social_app.sites.set([site])
