from api.encryption import decrypt_password
from django.db import models


class PasswordServicePair(models.Model):
    encrypted_password = models.BinaryField()
    service_name = models.CharField(max_length=255)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='passwords'
    )
    iv = models.BinaryField()

    class Meta:
        unique_together = ('service_name', 'encrypted_password', 'user')

    def get_password(self):
        return decrypt_password(
            self.encrypted_password,
            self.user.password,
            self.user.salt,
            self.iv
        )
