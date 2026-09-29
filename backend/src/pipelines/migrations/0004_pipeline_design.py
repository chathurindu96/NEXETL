from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("pipelines", "0003_align_pipeline_authoring_model")]
    operations = [
        migrations.CreateModel(name="PipelineDesignRecord", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("revision", models.PositiveIntegerField(default=1)), ("updated_at", models.DateTimeField(auto_now=True)), ("pipeline", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="design", to="pipelines.pipelinedefinitionrecord"))], options={"db_table": "nexetl_pipeline_design"}),
        migrations.CreateModel(name="PipelineDesignNodeRecord", fields=[("id", models.UUIDField(editable=False, primary_key=True, serialize=False)), ("type", models.CharField(max_length=12)), ("label", models.CharField(max_length=120)), ("connector_key", models.CharField(blank=True, max_length=64, null=True)), ("position_x", models.FloatField()), ("position_y", models.FloatField()), ("design", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="nodes", to="pipelines.pipelinedesignrecord"))], options={"db_table": "nexetl_pipeline_design_node"}),
        migrations.CreateModel(name="PipelineDesignEdgeRecord", fields=[("id", models.UUIDField(editable=False, primary_key=True, serialize=False)), ("source_node", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="outgoing_edges", to="pipelines.pipelinedesignnoderecord")), ("target_node", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="incoming_edges", to="pipelines.pipelinedesignnoderecord")), ("design", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="edges", to="pipelines.pipelinedesignrecord"))], options={"db_table": "nexetl_pipeline_design_edge"}),
        migrations.AddConstraint(model_name="pipelinedesignedgerecord", constraint=models.UniqueConstraint(fields=("design", "source_node", "target_node"), name="nexetl_design_unique_edge")),
    ]
