from django.apps import AppConfig
class ShopConfig(AppConfig):
    name = 'shop'
    def ready(self):
        try:
            import shop.signals
        except Exception:
            pass





class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        import shop.signals
