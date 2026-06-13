# Generated for the AI service knowledge base.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='KnowledgeBaseEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('category', models.CharField(blank=True, max_length=100)),
                ('intent', models.CharField(blank=True, max_length=100)),
                ('source_type', models.CharField(choices=[('product', 'Product'), ('category', 'Category'), ('policy', 'Policy'), ('faq', 'FAQ'), ('guide', 'Guide'), ('recommendation_rule', 'Recommendation Rule')], default='guide', max_length=30)),
                ('product_id', models.IntegerField(blank=True, null=True)),
                ('tags', models.TextField(blank=True)),
                ('priority', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'ai_knowledge_base',
                'ordering': ['-priority', 'category', 'title'],
            },
        ),
        migrations.AddIndex(
            model_name='knowledgebaseentry',
            index=models.Index(fields=['category'], name='ai_knowled_categor_e2e953_idx'),
        ),
        migrations.AddIndex(
            model_name='knowledgebaseentry',
            index=models.Index(fields=['intent'], name='ai_knowled_intent_82d8cd_idx'),
        ),
        migrations.AddIndex(
            model_name='knowledgebaseentry',
            index=models.Index(fields=['source_type'], name='ai_knowled_source__e885dd_idx'),
        ),
        migrations.AddIndex(
            model_name='knowledgebaseentry',
            index=models.Index(fields=['is_active'], name='ai_knowled_is_acti_849df2_idx'),
        ),
    ]
