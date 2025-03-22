from django.db import models


class Document(models.Model):

    document_types = (
        ('privacy_policy', 'Privacy policy'),
        ('user_agreement', 'User agreement'),
        ('2fauth', '2-factor Authentication'),
    )

    document_type = models.CharField("Тип документа", max_length=255, choices=document_types)
    attachment = models.FileField("Файл", upload_to="documents")

    class Meta:
        ordering = ['id',]
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self) -> str:
        return self.document_type

