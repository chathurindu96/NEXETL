from django.db import migrations, models


def backfill_names(apps, schema_editor):
    PipelineDefinitionRecord = apps.get_model("pipelines", "PipelineDefinitionRecord")
    for record in PipelineDefinitionRecord.objects.filter(name__isnull=True).iterator():
        record.name = f"Pipeline {str(record.id)[:8]}"
        record.save(update_fields=["name"])


class Migration(migrations.Migration):
    dependencies = [("pipelines", "0001_initial")]
    operations = [
        migrations.AddField(model_name="pipelinedefinitionrecord", name="name", field=models.CharField(max_length=120, null=True)),
        migrations.AddField(model_name="pipelinedefinitionrecord", name="description", field=models.TextField(blank=True, default="")),
        migrations.AddField(model_name="pipelinedefinitionrecord", name="state", field=models.CharField(default="DRAFT", max_length=12)),
        migrations.AddField(model_name="pipelinedefinitionrecord", name="created_at", field=models.DateTimeField(auto_now_add=True, null=True)),
        migrations.AddField(model_name="pipelinedefinitionrecord", name="updated_at", field=models.DateTimeField(auto_now=True, null=True)),
        migrations.RunPython(backfill_names, migrations.RunPython.noop),
        migrations.AlterField(model_name="pipelinedefinitionrecord", name="name", field=models.CharField(db_index=True, max_length=120)),
        migrations.AlterField(model_name="pipelinedefinitionrecord", name="state", field=models.CharField(db_index=True, default="DRAFT", max_length=12)),
        migrations.AlterField(model_name="pipelinedefinitionrecord", name="updated_at", field=models.DateTimeField(auto_now=True, db_index=True)),
    ]
