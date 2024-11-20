from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, ProjectCategory, Material, Condition, Toxicity, WasteType, Grade


@receiver(post_save, sender=Project)
def create_default_category_and_materials(sender, instance, created, **kwargs):
    if created:
        # Create the "Material" category linked to the project
        material_category = ProjectCategory.objects.create(
            project=instance,
            category='Material'
        )

        # Add two materials: "Tyre" and "Thermacol" to the Material category
        Material.objects.bulk_create([
            Material(name='PET', color='050C9C', category=material_category),
            Material(name='LDPE', color='CAF4FF', category=material_category),
            Material(name='Raffia', color='E5DDC5', category=material_category),
            Material(name='HDPE', color='850F8D', category=material_category),
            Material(name='PVC', color='C7B7A3', category=material_category),
            Material(name='PP', color='FFC96F', category=material_category),
            Material(name='MLP', color='FF0000', category=material_category),
            Material(name='thermacol', color='FFF7FC', category=material_category),
            Material(name='Rubber', color='94FFD8', category=material_category),
            Material(name='Tyre', color='31363F', category=material_category),
            Material(name='Paper', color='DAD3BE', category=material_category),
            Material(name='Cardboard', color='B7B597', category=material_category),
            Material(name='Metal', color='543310', category=material_category),
            Material(name='E-waste', color='FFFF80', category=material_category),
            Material(name='Glass', color='41B06E', category=material_category),
            Material(name='Textile', color='F72798', category=material_category),
        ])

        condition_category = ProjectCategory.objects.create(
            project=instance,
            category='Condition'
        )
        Condition.objects.bulk_create([
            Condition(name='Mixed', color='40A578', category=condition_category),
            Condition(name='Dirty', color='524C42', category=condition_category),
            Condition(name='Fair', color='F8EDFF', category=condition_category),
        ])

        toxicity_category = ProjectCategory.objects.create(
            project=instance,
            category='Toxicity'
        )
        Toxicity.objects.bulk_create([
            Toxicity(name='Toxic in', color='E72929', category=toxicity_category),
            Toxicity(name='Non toxic in', color='2C7865', category=toxicity_category),
        ])

        # Create "WasteType" category and related models
        waste_type_category = ProjectCategory.objects.create(
            project=instance,
            category='WasteType'
        )
        WasteType.objects.bulk_create([
            WasteType(name='FMCG', color='FF6500', category=waste_type_category),
            WasteType(name='Non FMCG', color='EBF400', category=waste_type_category),
        ])

        grade_type_category = ProjectCategory.objects.create(
            project=instance,
            category='Grade'
        )
        Grade.objects.bulk_create([
            Grade(name='Food Grade', color='FF9A00', category=grade_type_category),
            Grade(name='Non Food Grade', color='808836', category=grade_type_category),
        ])

