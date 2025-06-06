from django.db import models
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from barcode import get_barcode_class
from barcode.writer import ImageWriter
import logging


# Create your models here.


logger = logging.getLogger(__name__)

class Produto(models.Model):

    CATEGORIAS = [
        ('carnes', 'Carnes'),
        ('verduras', 'Verduras')
    ]
    FORMATOS = [
    ('code128', 'Code 128'),
    ('code39', 'Code 39'),
    ('ean13', 'EAN-13'),
    ('ean8', 'EAN-8'),
    ('upca', 'UPC-A'),
    ('jan', 'JAN'),
    ('isbn13', 'ISBN-13'),
    ('isbn10', 'ISBN-10'),
    ('issn', 'ISSN'),
    ('pzn', 'PZN'),
    ('ean14', 'EAN-14'),
    ('gs1_128', 'GS1-128'),
    ('itf', 'ITF'),
    ('codabar', 'Codabar'),
]

    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    imagem = models.ImageField(upload_to='produtos/', blank=True)   # foto do produto
    codigo = models.CharField(max_length=100, blank=True)  # código manual
    formato = models.CharField(max_length=20, choices=FORMATOS)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # verifica se é criação
        super().save(*args, **kwargs)  # salva inicialmente para obter ID

        # Gera o código de barras se o campo 'codigo' estiver preenchido
        if self.codigo:
            # Recria código se não existir imagem ou se DEBUG=True
            needs_gen = (not self.barcode_image) or settings.DEBUG
            if needs_gen:
                try:
                    barcode_class = get_barcode_class(self.formato)
                    barcode_obj = barcode_class(self.codigo, writer=ImageWriter())
                    buffer = BytesIO()
                    barcode_obj.write(buffer)
                    buffer.seek(0)
                    filename = f'barcode_{self.id}.png'
                    # Usa ContentFile para salvar o bytes no ImageField
                    self.barcode_image.save(filename, ContentFile(buffer.getvalue()), save=False)
                    super().save(update_fields=['barcode_image'])
                except Exception as e:
                    logger.error(f'Falha ao gerar código de barras para {self}: {e}')
        else:
            # Se não há código, removemos imagem existente (opcional)
            if self.barcode_image:
                self.barcode_image.delete(save=False)
        # Se código não preenchido e DEBUG, pode exibir 'Sem código' na interface