from django.apps import AppConfig
class ShopConfig(AppConfig):
    name = 'shop'
    def ready(self):
        try:
            import shop.signals
        except Exception:
            pass
