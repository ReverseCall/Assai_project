from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Produto

@receiver(post_delete, sender=Produto)
def deletar_arquivos_produto(sender, instance, **kwargs):
    if instance.imagem and instance.imagem.path:
        instance.imagem.delete(False)
    if instance.barcode_image and instance.barcode_image.path:
        instance.barcode_image.delete(False)
