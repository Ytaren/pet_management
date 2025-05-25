from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import ConsultationHistory

class Command(BaseCommand):
    help = '清理超过指定天数的咨询历史记录'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='清理超过多少天的记录（默认90天）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅预览将要删除的记录数量，不实际删除'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        if dry_run:
            # 仅计算将要删除的记录数
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            count = ConsultationHistory.objects.filter(created_at__lt=cutoff_date).count()
            self.stdout.write(
                self.style.WARNING(
                    f'预览模式：将要删除 {count} 条超过 {days} 天的咨询记录'
                )
            )
        else:
            # 实际删除记录
            deleted_count = ConsultationHistory.objects.cleanup_old_records(days=days)
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功删除了 {deleted_count} 条超过 {days} 天的咨询记录'
                )
            )
