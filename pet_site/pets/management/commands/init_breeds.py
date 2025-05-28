from django.core.management.base import BaseCommand
from pets.models import Breed


class Command(BaseCommand):
    help = '初始化宠物品种基础数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化宠物品种数据...')
        
        # 狗品种数据
        dog_breeds = [
            {'name': '拉布拉多', 'name_en': 'Labrador Retriever', 'average_lifespan': 12, 'average_weight_min': 25, 'average_weight_max': 36},
            {'name': '金毛寻回犬', 'name_en': 'Golden Retriever', 'average_lifespan': 12, 'average_weight_min': 25, 'average_weight_max': 34},
            {'name': '德国牧羊犬', 'name_en': 'German Shepherd', 'average_lifespan': 11, 'average_weight_min': 22, 'average_weight_max': 40},
            {'name': '边境牧羊犬', 'name_en': 'Border Collie', 'average_lifespan': 14, 'average_weight_min': 14, 'average_weight_max': 20},
            {'name': '柴犬', 'name_en': 'Shiba Inu', 'average_lifespan': 13, 'average_weight_min': 8, 'average_weight_max': 11},
            {'name': '萨摩耶', 'name_en': 'Samoyed', 'average_lifespan': 13, 'average_weight_min': 16, 'average_weight_max': 30},
            {'name': '哈士奇', 'name_en': 'Siberian Husky', 'average_lifespan': 13, 'average_weight_min': 16, 'average_weight_max': 27},
            {'name': '比熊犬', 'name_en': 'Bichon Frise', 'average_lifespan': 14, 'average_weight_min': 5, 'average_weight_max': 10},
            {'name': '泰迪', 'name_en': 'Poodle', 'average_lifespan': 14, 'average_weight_min': 3, 'average_weight_max': 32},
            {'name': '博美', 'name_en': 'Pomeranian', 'average_lifespan': 14, 'average_weight_min': 1.4, 'average_weight_max': 3.2},
            {'name': '吉娃娃', 'name_en': 'Chihuahua', 'average_lifespan': 15, 'average_weight_min': 1, 'average_weight_max': 3},
            {'name': '法国斗牛犬', 'name_en': 'French Bulldog', 'average_lifespan': 11, 'average_weight_min': 8, 'average_weight_max': 14},
            {'name': '英国斗牛犬', 'name_en': 'English Bulldog', 'average_lifespan': 8, 'average_weight_min': 18, 'average_weight_max': 25},
            {'name': '京巴犬', 'name_en': 'Pekingese', 'average_lifespan': 13, 'average_weight_min': 3, 'average_weight_max': 6},
            {'name': '中华田园犬', 'name_en': 'Chinese Rural Dog', 'average_lifespan': 15, 'average_weight_min': 10, 'average_weight_max': 25},
        ]

        # 猫品种数据
        cat_breeds = [
            {'name': '英国短毛猫', 'name_en': 'British Shorthair', 'average_lifespan': 15, 'average_weight_min': 3, 'average_weight_max': 8},
            {'name': '美国短毛猫', 'name_en': 'American Shorthair', 'average_lifespan': 15, 'average_weight_min': 3, 'average_weight_max': 7},
            {'name': '波斯猫', 'name_en': 'Persian', 'average_lifespan': 14, 'average_weight_min': 3, 'average_weight_max': 6},
            {'name': '暹罗猫', 'name_en': 'Siamese', 'average_lifespan': 15, 'average_weight_min': 2.5, 'average_weight_max': 5},
            {'name': '布偶猫', 'name_en': 'Ragdoll', 'average_lifespan': 13, 'average_weight_min': 4, 'average_weight_max': 9},
            {'name': '缅因猫', 'name_en': 'Maine Coon', 'average_lifespan': 13, 'average_weight_min': 4, 'average_weight_max': 8},
            {'name': '苏格兰折耳猫', 'name_en': 'Scottish Fold', 'average_lifespan': 13, 'average_weight_min': 2.5, 'average_weight_max': 6},
            {'name': '俄罗斯蓝猫', 'name_en': 'Russian Blue', 'average_lifespan': 15, 'average_weight_min': 3, 'average_weight_max': 5.5},
            {'name': '孟加拉猫', 'name_en': 'Bengal', 'average_lifespan': 14, 'average_weight_min': 3, 'average_weight_max': 7},
            {'name': '阿比西尼亚猫', 'name_en': 'Abyssinian', 'average_lifespan': 14, 'average_weight_min': 3, 'average_weight_max': 5},
            {'name': '橘猫', 'name_en': 'Orange Tabby', 'average_lifespan': 15, 'average_weight_min': 3, 'average_weight_max': 7},
            {'name': '狸花猫', 'name_en': 'Chinese Li Hua', 'average_lifespan': 16, 'average_weight_min': 3, 'average_weight_max': 6},
            {'name': '中华田园猫', 'name_en': 'Chinese Domestic Cat', 'average_lifespan': 16, 'average_weight_min': 2.5, 'average_weight_max': 6},
        ]

        # 其他宠物品种数据
        other_breeds = [
            # 兔子
            {'name': '荷兰侏儒兔', 'name_en': 'Netherland Dwarf', 'pet_type': 'rabbit', 'average_lifespan': 10, 'average_weight_min': 0.5, 'average_weight_max': 1.2},
            {'name': '垂耳兔', 'name_en': 'Holland Lop', 'pet_type': 'rabbit', 'average_lifespan': 9, 'average_weight_min': 1, 'average_weight_max': 2},
            {'name': '安哥拉兔', 'name_en': 'Angora Rabbit', 'pet_type': 'rabbit', 'average_lifespan': 8, 'average_weight_min': 2, 'average_weight_max': 4},
            
            # 仓鼠
            {'name': '金丝熊', 'name_en': 'Golden Hamster', 'pet_type': 'hamster', 'average_lifespan': 3, 'average_weight_min': 0.08, 'average_weight_max': 0.15},
            {'name': '三线仓鼠', 'name_en': 'Chinese Hamster', 'pet_type': 'hamster', 'average_lifespan': 2, 'average_weight_min': 0.03, 'average_weight_max': 0.08},
            
            # 鸟类
            {'name': '虎皮鹦鹉', 'name_en': 'Budgerigar', 'pet_type': 'bird', 'average_lifespan': 8, 'average_weight_min': 0.03, 'average_weight_max': 0.04},
            {'name': '玄凤鹦鹉', 'name_en': 'Cockatiel', 'pet_type': 'bird', 'average_lifespan': 20, 'average_weight_min': 0.08, 'average_weight_max': 0.1},
            {'name': '文鸟', 'name_en': 'Java Sparrow', 'pet_type': 'bird', 'average_lifespan': 8, 'average_weight_min': 0.02, 'average_weight_max': 0.03},
        ]

        created_count = 0

        # 创建狗品种
        for breed_data in dog_breeds:
            breed, created = Breed.objects.get_or_create(
                name=breed_data['name'],
                pet_type='dog',
                defaults={
                    'name_en': breed_data.get('name_en', ''),
                    'average_lifespan': breed_data.get('average_lifespan'),
                    'average_weight_min': breed_data.get('average_weight_min'),
                    'average_weight_max': breed_data.get('average_weight_max'),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'创建狗品种: {breed.name}')

        # 创建猫品种
        for breed_data in cat_breeds:
            breed, created = Breed.objects.get_or_create(
                name=breed_data['name'],
                pet_type='cat',
                defaults={
                    'name_en': breed_data.get('name_en', ''),
                    'average_lifespan': breed_data.get('average_lifespan'),
                    'average_weight_min': breed_data.get('average_weight_min'),
                    'average_weight_max': breed_data.get('average_weight_max'),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'创建猫品种: {breed.name}')

        # 创建其他宠物品种
        for breed_data in other_breeds:
            breed, created = Breed.objects.get_or_create(
                name=breed_data['name'],
                pet_type=breed_data['pet_type'],
                defaults={
                    'name_en': breed_data.get('name_en', ''),
                    'average_lifespan': breed_data.get('average_lifespan'),
                    'average_weight_min': breed_data.get('average_weight_min'),
                    'average_weight_max': breed_data.get('average_weight_max'),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'创建{breed.get_pet_type_display()}品种: {breed.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'数据初始化完成！共创建了 {created_count} 个品种记录。'
            )
        )
