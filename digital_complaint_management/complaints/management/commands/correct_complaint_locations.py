import json
import urllib.request
import urllib.parse
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from complaints.models import Complaint

class Command(BaseCommand):
    help = "Inspects and safely corrects existing complaint geolocation coordinates using Google Geocoding API."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate location verification and geocoding without altering the database.'
        )
        parser.add_argument(
            '--complaint-id',
            type=str,
            default=None,
            help='Process a specific complaint ID only (e.g. RN-2026-000009).'
        )
        parser.add_argument(
            '--force-default',
            action='store_true',
            help='Geocode and correct complaints currently holding the default Bangalore coordinates (12.9716, 77.5946).'
        )

    def geocode_address(self, address):
        """
        Geocodes an address string using Google Geocoding API if API key is configured,
        or OpenStreetMap Nominatim as fallback.
        Returns (lat, lng, formatted_address) or None.
        """
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        if api_key and str(api_key).strip() and str(api_key).strip() != 'YOUR_GOOGLE_MAPS_API_KEY':
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address)}&key={api_key}"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'ResolveNow/1.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    if data.get('status') == 'OK' and data.get('results'):
                        result = data['results'][0]
                        loc = result['geometry']['location']
                        return Decimal(str(round(loc['lat'], 7))), Decimal(str(round(loc['lng'], 7))), result.get('formatted_address', address)
                    else:
                        self.stdout.write(self.style.WARNING(f"Google Geocoding status: {data.get('status')} for '{address}'"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Google Geocoding error for '{address}': {e}"))

        # Fallback to OpenStreetMap Nominatim geocoder
        nom_url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(address)}&limit=1"
        try:
            req = urllib.request.Request(nom_url, headers={'User-Agent': 'ResolveNow-CivicPortal/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                nom_data = json.loads(response.read().decode())
                if nom_data:
                    lat = Decimal(str(round(float(nom_data[0]['lat']), 7)))
                    lng = Decimal(str(round(float(nom_data[0]['lon']), 7)))
                    return lat, lng, nom_data[0].get('display_name', address)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Fallback geocoding error for '{address}': {e}"))

        return None

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        target_id = options['complaint_id']
        force_default = options['force_default']

        self.stdout.write("========================================================")
        self.stdout.write("ResolveNow – Complaint Location Inspection & Correction")
        self.stdout.write("========================================================")

        queryset = Complaint.objects.all().order_by('complaint_id')
        if target_id:
            queryset = queryset.filter(complaint_id=target_id.strip().upper())

        total = queryset.count()
        self.stdout.write(f"Inspecting {total} complaint record(s)...\n")

        valid_count = 0
        corrected_count = 0
        missing_count = 0

        for c in queryset:
            addr = (c.location_address or '').strip()
            lat = c.latitude
            lng = c.longitude

            is_default = False
            if lat is not None and lng is not None:
                # Check if exact default Bangalore coordinates
                if abs(float(lat) - 12.9716) < 0.0001 and abs(float(lng) - 77.5946) < 0.0001:
                    is_default = True

            needs_correction = False
            reason = ""

            if lat is None or lng is None:
                needs_correction = True
                reason = "Missing coordinates"
                missing_count += 1
            elif not (-90.0 <= float(lat) <= 90.0 and -180.0 <= float(lng) <= 180.0):
                needs_correction = True
                reason = "Out-of-range coordinates"
            elif is_default and (force_default or target_id):
                needs_correction = True
                reason = "Default fallback coordinates (12.9716, 77.5946)"
            else:
                valid_count += 1

            if needs_correction and addr:
                self.stdout.write(f"[{c.complaint_id}] {reason}: '{addr[:60]}...'")
                geo_res = self.geocode_address(addr)
                if geo_res:
                    new_lat, new_lng, formatted_addr = geo_res
                    self.stdout.write(
                        self.style.SUCCESS(f"  -> Resolved to: Lat {new_lat}, Lng {new_lng}")
                    )
                    if not dry_run:
                        c.latitude = new_lat
                        c.longitude = new_lng
                        # If address was short or unformatted, update with formatted
                        if formatted_addr and len(formatted_addr) > len(c.location_address or ''):
                            c.location_address = formatted_addr
                        c.save(update_fields=['latitude', 'longitude', 'location_address'])
                        corrected_count += 1
                    else:
                        self.stdout.write("  [Dry Run] Changes not written to DB.")
                else:
                    self.stdout.write(self.style.ERROR("  -> Geocoding failed or returned no results."))
            elif needs_correction and not addr:
                self.stdout.write(self.style.WARNING(f"[{c.complaint_id}] Missing both coordinates and address. Flagged for admin correction."))

        self.stdout.write("\n========================================================")
        self.stdout.write(f"Inspection Summary:")
        self.stdout.write(f"  Total Complaints: {total}")
        self.stdout.write(f"  Already Valid:    {valid_count}")
        self.stdout.write(f"  Corrected:        {corrected_count} (Dry Run: {dry_run})")
        self.stdout.write("========================================================")
