from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("pipelines", "0002_pipeline_authoring_metadata")]
    operations = [
        migrations.AlterModelOptions(name="pipelinedefinitionrecord", options={"permissions": (("register_pipeline_definition", "Can register pipeline definition"), ("inspect_pipeline_definition", "Can inspect pipeline definition"), ("list_pipeline_definition", "Can list pipeline definitions"), ("update_pipeline_definition", "Can update pipeline definitions"), ("archive_pipeline_definition", "Can archive pipeline definitions"), ("design_pipeline_definition", "Can design pipeline definitions"))}),
        migrations.AlterField(model_name="pipelinedefinitionrecord", name="created_at", field=models.DateTimeField(auto_now_add=True)),
    ]
