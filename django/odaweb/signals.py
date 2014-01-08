from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from odaweb.disassembler import Disassembler
from odaweb.models import BinaryString


@receiver(post_save, sender=BinaryString)
def binary_string_update(sender, instance, **kwargs):
    Disassembler(instance).analyze_first_time()