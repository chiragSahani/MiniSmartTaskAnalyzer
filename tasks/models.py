from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(help_text="Estimated effort in hours")
    importance = models.IntegerField(default=5, help_text="1-10 scale")
    dependencies = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="dependents")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def to_dict(self):

        return {
            'id': self.id,
            'title': self.title,
            'due_date': self.due_date,
            'estimated_hours': self.estimated_hours,
            'importance': self.importance,
            'dependencies': [d.id for d in self.dependencies.all()]
        }
