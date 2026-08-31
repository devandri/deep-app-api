from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
    """Queryset with soft delete functionality"""
    
    def delete(self):
        return self.update(deleted_at=timezone.now())
    
    def hard_delete(self):
        return super().delete()
    
    def restore(self):
        return self.update(deleted_at=None)
    
    def only_deleted(self):
        return self.filter(deleted_at__isnull=False)
    
class SoftDeleteManager(UserManager):
    """Manager that by automatically filtering soft delete"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model).filter(deleted_at__isnull=True)
    
    def all_objects(self):
        return SoftDeleteQuerySet(self.model)
    
    def only_deleted(self):
        return SoftDeleteQuerySet(self.model).filter(deleted_at__isnull=False)

class User(AbstractUser):
    
    deleted_at = models.CharField(null=True, blank=True, db_index=True)
    
    # override default manager
    objects = SoftDeleteManager()
    
    # Manager for accessing the entire data
    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
        
    def __str__(self):
        return self.username
    
    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])
        
    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)
        
    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])
        
    @property
    def is_deleted(self):
        return self.deleted_at is not None
