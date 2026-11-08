from django.test import SimpleTestCase


class ClassifyTests(SimpleTestCase):
    def get(self, text):
        return self.client.get("/classify/", {"string": text})

    def test_promo(self):
        r = self.get("Paket internet 10GB hanya Rp25.000, aktifkan sekarang di *123# berlaku 30 hari")
        self.assertEqual(r.status_code, 200)
        self.assertIn(r.content.decode(), {"normal", "promo", "spam"})

    def test_labels(self):
        self.assertEqual(self.get("Mama minta pulsa 50rb ke nomor ini dulu ya, nanti mama ganti").content.decode(), "spam")
        self.assertEqual(self.get("nanti malam jadi makan bareng ga? aku otw jam 7").content.decode(), "normal")

    def test_missing_string(self):
        self.assertEqual(self.client.get("/classify/").status_code, 400)
